# fix_iot_capture — M48 capture audit (2026-11-17): the records the spec's
# sub-modules capture that had no model, and the decisions that had no writer.
#
# - Stream Registry & Onboarding: signal definition (FR-IOT-004), criticality
#   assessment / monitoring scope (FR-IOT-007, BRU-IOT-20), device identity
#   (firmware, connectivity, gateway: FR-IOT-002) and decommissioning (FR-IOT-008).
# - Protocol Adapters: Sparkplug B, SNMP, file batch and AEMP telematics channels
#   (FR-IOT-009/012/014/015), a source address per stream (FR-IOT-013), and the
#   file batch import (FR-IOT-012), which goes through the live ingest gates.
# - Ingestion: a quality flag instead of a silent pass (FR-IOT-016).
# - Threshold Alerting: maintenance windows with an approver and an expiry
#   (FR-IOT-032, BRU-IOT-16).
# - Health Scoring: an asset health index history with band and trend
#   (FR-IOT-037/038, AUT-IOT-11).
# - Failure Prediction: failure mode and the RUL interval (FR-IOT-039/041), and
#   the outcome of a prediction no intervention acted on (FR-IOT-044, BRU-IOT-14).
# - Prescriptive Routing: parts (M15) and skill (M22) on the intervention
#   (FR-IOT-042).
import base64
import csv
import io
import logging
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

from .fix_iot_ops import (
    IOT_ADMIN,
    IOT_MANAGER,
    IOT_OPERATOR,
    IngestRefused,
    _require_role,
)

_logger = logging.getLogger(__name__)

CRITICALITY = [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")]
HEALTH_BANDS = [
    ("healthy", "Healthy"),
    ("watch", "Watch"),
    ("degraded", "Degraded"),
    ("critical", "Critical"),
]
_BAND_RANK = {"healthy": 0, "watch": 1, "degraded": 2, "critical": 3}
# A maintenance window is a bounded suppression (BRU-IOT-16): never open-ended.
MAX_WINDOW_DAYS = 30
# A file batch is read in one transaction; a bigger export is split by the sender.
MAX_BATCH_ROWS = 5000


def _band(score):
    if score >= 80:
        return "healthy"
    if score >= 55:
        return "watch"
    if score >= 30:
        return "degraded"
    return "critical"


def _text(value):
    return (value or "").strip()


# ---------------------------------------------------------------------------
# Stream Registry & Onboarding
# ---------------------------------------------------------------------------
class FixIotSignal(models.Model):
    """FR-IOT-004: what a stream measures, its unit, expected range, sampling
    interval, criticality and retention class. A stream that names a signal
    takes its metric, unit and interval from it, and ingest flags a reading
    outside the expected range instead of passing it silently (FR-IOT-016)."""

    _name = "fix.iot.signal"
    _description = "IoT Signal Definition"
    _order = "code"
    _rec_name = "code"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    code = fields.Char(
        required=True, help="The metric name the readings carry, e.g. disk_temp_c, vibration_rms"
    )
    name = fields.Char(required=True)
    data_type = fields.Selection(
        [
            ("gauge", "Gauge (a level)"),
            ("counter", "Counter (always rising)"),
            ("flag", "On / Off"),
        ],
        required=True,
        default="gauge",
    )
    canonical_unit = fields.Char(string="Canonical Unit", help="e.g. C, mm/s, %, kWh")
    expected_min = fields.Float(string="Expected Minimum")
    expected_max = fields.Float(string="Expected Maximum")
    has_range = fields.Boolean(
        string="Range Checked",
        help="Readings outside the expected minimum and maximum are flagged out of range.",
    )
    sampling_interval_sec = fields.Integer(
        string="Sampling Interval (s)", default=60, required=True
    )
    criticality_class = fields.Selection(CRITICALITY, required=True, default="medium")
    retention_class = fields.Selection(
        [
            ("short", "Short (raw 30 days)"),
            ("standard", "Standard (raw 90 days)"),
            ("long", "Long (raw 365 days)"),
        ],
        required=True,
        default="standard",
    )
    active = fields.Boolean(default=True)
    stream_count = fields.Integer(compute="_compute_stream_count", string="Streams")

    _code_company_unique = models.Constraint(
        "UNIQUE (company_id, code)", "A signal code is defined once per company."
    )
    _interval_positive = models.Constraint(
        "CHECK (sampling_interval_sec > 0)", "The sampling interval must be positive."
    )

    @api.constrains("has_range", "expected_min", "expected_max")
    def _check_range(self):
        for rec in self:
            if rec.has_range and rec.expected_max < rec.expected_min:
                raise ValidationError(
                    "Signal %s: the expected maximum is below the minimum." % rec.code
                )

    @api.constrains("code")
    def _check_code(self):
        for rec in self:
            if not _text(rec.code) or " " in _text(rec.code):
                raise ValidationError("A signal code is one word, e.g. disk_temp_c.")

    def _compute_stream_count(self):
        Stream = self.env["fix.iot.stream"]
        for rec in self:
            rec.stream_count = Stream.search_count([("signal_id", "=", rec.id)]) if rec.id else 0

    @api.model_create_multi
    def create(self, vals_list):
        _require_role(self.env, IOT_ADMIN, "Defining a signal")
        for vals in vals_list:
            if vals.get("code"):
                vals["code"] = vals["code"].strip()
        return super().create(vals_list)

    def write(self, vals):
        _require_role(self.env, IOT_ADMIN, "Changing a signal definition")
        if "code" in vals and any(
            rec.code != _text(vals["code"]) and rec.stream_count for rec in self
        ):
            raise UserError(
                "A signal that streams already carry keeps its code: their readings are "
                "stored under it. Define a new signal instead."
            )
        return super().write(vals)

    def _fix_out_of_range(self, value):
        self.ensure_one()
        return bool(self.has_range and not (self.expected_min <= value <= self.expected_max))


class FixIotMonitoringScope(models.Model):
    """FR-IOT-007 / BRU-IOT-20 (ISO 17359): an asset is monitored because its
    failure matters, recorded before collection grows by accident. The scope
    names the asset (M45 equipment or M47 site), how critical it is, what its
    failure costs, which signals are collected and why, and when it is reviewed.
    Health is scored for the devices on the assets in an active scope."""

    _name = "fix.iot.monitoring.scope"
    _description = "IoT Monitoring Scope (Criticality Assessment)"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "review_due, id desc"

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"assessed_by_id"}

    name = fields.Char(required=True, default="New", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    equipment_id = fields.Many2one("fix.equipment", string="Equipment (M45)", ondelete="restrict")
    site_id = fields.Many2one("fix.site", string="Site (M47)", ondelete="restrict")
    criticality = fields.Selection(CRITICALITY, required=True, default="medium", tracking=True)
    failure_consequence = fields.Text(
        string="Failure Consequence",
        help="What a failure of this asset costs: safety, downtime, customers, money.",
    )
    signal_ids = fields.Many2many("fix.iot.signal", string="Signals Selected")
    selection_rationale = fields.Text(string="Why These Signals")
    assessed_by_id = fields.Many2one("res.users", string="Assessed By", readonly=True, copy=False)
    assessed_on = fields.Date(
        string="Assessed On", required=True, default=fields.Date.context_today
    )
    review_due = fields.Date(string="Review Due", required=True, tracking=True)
    active = fields.Boolean(default=True, tracking=True)
    device_count = fields.Integer(compute="_compute_devices", string="Devices")
    health_ids = fields.One2many("fix.iot.health", "scope_id", string="Health History")
    last_scored_on = fields.Datetime(compute="_compute_last_score", string="Last Scored")
    worst_band = fields.Selection(HEALTH_BANDS, compute="_compute_last_score", string="Worst Band")

    # The workspace leaves an empty field out of the values it saves, and a
    # constraint runs only when one of its fields is saved: each check also
    # names a required field, so it runs on every create.
    @api.constrains("equipment_id", "site_id", "criticality")
    def _check_subject(self):
        for rec in self:
            if bool(rec.equipment_id) == bool(rec.site_id):
                raise ValidationError(
                    "A monitoring scope assesses one asset: name the M45 equipment or the "
                    "M47 site, not both and not neither (BRU-IOT-02)."
                )

    @api.constrains("assessed_on", "review_due")
    def _check_review(self):
        for rec in self:
            if rec.review_due and rec.assessed_on and rec.review_due <= rec.assessed_on:
                raise ValidationError("The review falls due after the assessment date.")

    @api.constrains("failure_consequence", "selection_rationale", "criticality")
    def _check_reasoned(self):
        for rec in self:
            if not _text(rec.failure_consequence) or not _text(rec.selection_rationale):
                raise ValidationError(
                    "A criticality assessment records what a failure costs and why these "
                    "signals are collected (ISO 17359): monitoring scope is a decision, "
                    "not an accident (BRU-IOT-20)."
                )

    @api.model_create_multi
    def create(self, vals_list):
        _require_role(self.env, IOT_ADMIN, "Recording a criticality assessment")
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.iot.monitoring.scope") or "IMSC/New"
                )
        records = super().create(vals_list)
        for rec in records:
            rec._guarded().write({"assessed_by_id": self.env.uid})
        return records

    def write(self, vals):
        if not self.env.su:
            _require_role(self.env, IOT_ADMIN, "Changing a criticality assessment")
        return super().write(vals)

    def _fix_devices(self):
        self.ensure_one()
        domain = [("decommissioned", "=", False)]
        if self.equipment_id:
            domain.append(("equipment_id", "=", self.equipment_id.id))
        else:
            domain.append(("site_id", "=", self.site_id.id))
        return self.env["fix.iot.device"].sudo().search(domain)

    def _compute_devices(self):
        for rec in self:
            rec.device_count = len(rec._fix_devices()) if (rec.equipment_id or rec.site_id) else 0

    def _compute_last_score(self):
        for rec in self:
            latest = rec.health_ids.sorted("computed_at", reverse=True)
            rec.last_scored_on = latest[:1].computed_at
            last_run = latest.filtered(lambda h, at=latest[:1].computed_at: h.computed_at == at)
            rec.worst_band = (
                max(last_run.mapped("band"), key=lambda b: _BAND_RANK[b]) if last_run else False
            )

    def action_score_now(self):
        """Score the health of every device on this scope's asset now (the
        nightly job does the same for every active scope)."""
        _require_role(self.env, IOT_OPERATOR, "Scoring asset health")
        written = self.env["fix.iot.health"]
        for rec in self:
            if not rec.active:
                raise UserError("Scope %s is archived: restore it before scoring." % rec.name)
            devices = rec._fix_devices()
            if not devices:
                raise UserError(
                    "Scope %s has no device on its asset to score: register the device "
                    "and bind it to the equipment or site first." % rec.name
                )
            written |= self.env["fix.iot.health"]._fix_score(devices, rec)
        return True

    @api.model
    def cron_health(self):
        """AUT-IOT-11: nightly, score every device of every active scope.
        A failure on one scope keeps the previous index and moves on."""
        count = 0
        for scope in self.sudo().search([]):
            devices = scope._fix_devices()
            if not devices:
                continue
            try:
                with self.env.cr.savepoint():
                    count += len(self.env["fix.iot.health"]._fix_score(devices, scope))
            except Exception:
                # AUT-IOT-11: keep the previous index, report, score the rest.
                _logger.exception("M48 health scoring failed for scope %s", scope.name)
        return count


class FixIotHealth(models.Model):
    """FR-IOT-037/038: the asset health index as history, so the trajectory
    is reported and not only the current value. Written by scoring, never
    typed. The rule is the transparent one of the Asset Health report: 100,
    minus 12 per open alert (at most 60), minus 15 degraded / 30 offline,
    minus 20 when no reading arrived in 24 hours."""

    _name = "fix.iot.health"
    _description = "IoT Asset Health Index"
    _inherit = ["fix.iot.insert.only.mixin"]
    _order = "computed_at desc, id desc"

    scope_id = fields.Many2one(
        "fix.iot.monitoring.scope", string="Scope", ondelete="set null", index=True
    )
    device_id = fields.Many2one(
        "fix.iot.device", string="Device", required=True, ondelete="cascade", index=True
    )
    equipment_id = fields.Many2one(related="device_id.equipment_id", store=True, string="Equipment")
    site_id = fields.Many2one(related="device_id.site_id", store=True, string="Site")
    company_id = fields.Many2one(
        related="device_id.company_id", store=True, index=True, string="Company"
    )
    computed_at = fields.Datetime(string="Scored At", required=True)
    index_value = fields.Integer(string="Health Index", required=True)
    band = fields.Selection(HEALTH_BANDS, required=True)
    previous_index = fields.Integer(string="Previous Index")
    trend = fields.Selection(
        [
            ("first", "First Score"),
            ("improving", "Improving"),
            ("stable", "Stable"),
            ("worsening", "Worsening"),
        ],
        required=True,
    )
    open_alerts = fields.Integer(string="Open Alerts")
    readings_24h = fields.Integer(string="Readings 24h")
    device_status = fields.Char(string="Device Status")
    factors = fields.Text(string="Contributing Factors")

    @api.model
    def _fix_score(self, devices, scope=None):
        now = fields.Datetime.now()
        since = now - timedelta(hours=24)
        Alert = self.env["fix.iot.alert"].sudo()
        Telemetry = self.env["fix.iot.telemetry"].sudo()
        written = self.browse()
        for device in devices.sudo():
            alerts = Alert.search_count(
                [("device_id", "=", device.id), ("state", "!=", "resolved")]
            )
            readings = Telemetry.search_count(
                [
                    ("device_id", "=", device.id),
                    ("timestamp", ">=", since),
                    ("timestamp", "<=", now),
                ]
            )
            factors = []
            score = 100
            alert_cut = min(alerts * 12, 60)
            if alert_cut:
                score -= alert_cut
                factors.append("-%d: %d open alert(s)" % (alert_cut, alerts))
            if device.status == "degraded":
                score -= 15
                factors.append("-15: device degraded")
            elif device.status == "offline":
                score -= 30
                factors.append("-30: device offline")
            if not readings:
                score -= 20
                factors.append("-20: no reading in 24 hours")
            score = max(min(score, 100), 0)
            band = _band(score)
            previous = self.sudo().search(
                [("device_id", "=", device.id)], order="computed_at desc, id desc", limit=1
            )
            if not previous:
                trend = "first"
            elif score > previous.index_value + 5:
                trend = "improving"
            elif score < previous.index_value - 5:
                trend = "worsening"
            else:
                trend = "stable"
            rec = (
                self.sudo()
                ._guarded()
                .create(
                    {
                        "scope_id": scope.id if scope else False,
                        "device_id": device.id,
                        "computed_at": now,
                        "index_value": score,
                        "band": band,
                        "previous_index": previous.index_value if previous else 0,
                        "trend": trend,
                        "open_alerts": alerts,
                        "readings_24h": readings,
                        "device_status": dict(device._fields["status"].selection).get(
                            device.status
                        ),
                        "factors": "; ".join(factors)
                        or "No deduction: no open alert, online, reporting.",
                    }
                )
            )
            payload = {
                "device": device.device_id,
                "equipment_id": device.equipment_id.id or False,
                "site_id": device.site_id.id or False,
                "index": score,
                "band": band,
                "trend": trend,
                "factors": rec.factors,
            }
            publish(self.env, "asset.health_updated", "fix.iot.health", rec.id, payload)
            if previous and _BAND_RANK[band] > _BAND_RANK[previous.band]:
                publish(
                    self.env,
                    "asset.health_degraded",
                    "fix.iot.health",
                    rec.id,
                    dict(payload, from_band=previous.band),
                )
            written |= rec
        return written


class FixIotDeviceCapture(models.Model):
    """FR-IOT-002: a device or gateway is registered with its firmware,
    connectivity and the gateway it reports through. FR-IOT-008: it is
    decommissioned, never deleted, and its streams with it."""

    _inherit = "fix.iot.device"

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "decommissioned",
            "decommissioned_on",
            "decommissioned_by",
            "decommission_reason",
        }

    firmware = fields.Char(string="Firmware Version")
    connectivity = fields.Selection(
        [
            ("ethernet", "Ethernet"),
            ("wifi", "Wi-Fi"),
            ("cellular", "Cellular (2G/4G)"),
            ("lorawan", "LoRaWAN"),
            ("serial", "Serial / Modbus"),
            ("file", "Periodic File Export"),
        ],
        string="Connectivity",
    )
    gateway_id = fields.Many2one(
        "fix.iot.device",
        string="Reports Through Gateway",
        ondelete="set null",
        domain=[("device_type", "=", "gateway")],
    )
    serial_no = fields.Char(string="Serial Number")
    installed_on = fields.Date(string="Installed On")
    decommissioned = fields.Boolean(readonly=True, copy=False, index=True)
    decommissioned_on = fields.Datetime(string="Decommissioned On", readonly=True, copy=False)
    decommissioned_by = fields.Many2one(
        "res.users", string="Decommissioned By", readonly=True, copy=False
    )
    decommission_reason = fields.Char(string="Why Decommissioned", readonly=True, copy=False)

    @api.constrains("gateway_id")
    def _check_gateway(self):
        for rec in self:
            if rec.gateway_id and (
                rec.gateway_id == rec or rec.gateway_id.device_type != "gateway"
            ):
                raise ValidationError(
                    "Device %s reports through a gateway: choose another device registered "
                    "as a gateway." % rec.name
                )

    @api.constrains("device_id", "company_id")
    def _check_identifier_unique(self):
        for rec in self:
            if self.sudo().search_count(
                [
                    ("device_id", "=", rec.device_id),
                    ("company_id", "=", rec.company_id.id),
                    ("id", "!=", rec.id),
                ]
            ):
                raise ValidationError(
                    "Device identifier %s is already registered: one record per physical "
                    "device (FR-IOT-002)." % rec.device_id
                )

    def action_decommission(self, reason=None):
        """Stop the device: its streams are decommissioned (ingestion stops,
        open gaps and alerts close) and it accepts no new stream."""
        _require_role(self.env, IOT_ADMIN, "Decommissioning a device")
        why = _text(reason)
        if not why:
            raise UserError("Give the reason for decommissioning the device.")
        now = fields.Datetime.now()
        for rec in self:
            if rec.decommissioned:
                raise UserError("Device %s is already decommissioned." % rec.name)
            streams = (
                self.env["fix.iot.stream"]
                .sudo()
                .search([("device_id", "=", rec.id), ("state", "!=", "decommissioned")])
            )
            streams._fix_decommission("device %s decommissioned: %s" % (rec.name, why))
            rec._guarded().write(
                {
                    "decommissioned": True,
                    "decommissioned_on": now,
                    "decommissioned_by": self.env.uid,
                    "decommission_reason": why,
                }
            )
        return True


class FixIotStreamCapture(models.Model):
    _inherit = "fix.iot.stream"

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "decommissioned_on",
            "decommissioned_by",
            "decommission_reason",
        }

    signal_id = fields.Many2one(
        "fix.iot.signal",
        string="Signal",
        ondelete="restrict",
        help="The signal definition: the stream takes its metric, unit and interval from it, "
        "and readings outside its expected range are flagged.",
    )
    source_address = fields.Char(
        string="Source Address",
        help="Where the adapter finds this signal: the MQTT topic, the OPC UA node id, the "
        "SNMP OID or the file column.",
    )
    state = fields.Selection(
        selection_add=[("decommissioned", "Decommissioned")],
        ondelete={"decommissioned": "set default"},
    )
    decommissioned_on = fields.Datetime(string="Decommissioned On", readonly=True, copy=False)
    decommissioned_by = fields.Many2one(
        "res.users", string="Decommissioned By", readonly=True, copy=False
    )
    decommission_reason = fields.Char(string="Why Decommissioned", readonly=True, copy=False)

    @staticmethod
    def _fix_from_signal(vals, signal):
        vals["metric"] = signal.code
        if signal.canonical_unit and not vals.get("unit"):
            vals["unit"] = signal.canonical_unit
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        Device = self.env["fix.iot.device"].sudo()
        Signal = self.env["fix.iot.signal"].sudo()
        for vals in vals_list:
            if vals.get("device_id") and Device.browse(vals["device_id"]).decommissioned:
                raise UserError("The device is decommissioned: it takes no new stream.")
            if vals.get("signal_id"):
                signal = Signal.browse(vals["signal_id"])
                self._fix_from_signal(vals, signal)
                if "sample_interval_sec" not in vals:
                    vals["sample_interval_sec"] = signal.sampling_interval_sec
        return super().create(vals_list)

    def write(self, vals):
        if vals.get("signal_id"):
            signal = self.env["fix.iot.signal"].sudo().browse(vals["signal_id"])
            vals = self._fix_from_signal(dict(vals), signal)
        return super().write(vals)

    @api.constrains("signal_id", "metric")
    def _check_signal_metric(self):
        for rec in self:
            if rec.signal_id and rec.metric != rec.signal_id.code:
                raise ValidationError(
                    "Stream %s carries signal %s: its metric is the signal's code."
                    % (rec.name, rec.signal_id.code)
                )

    def action_activate(self):
        for rec in self:
            if rec.state == "decommissioned":
                raise UserError(
                    "Stream %s is decommissioned: its series is terminated. Register a new "
                    "stream." % rec.name
                )
            if rec.device_id.decommissioned:
                raise UserError("Device %s is decommissioned." % rec.device_id.name)
        return super().action_activate()

    def action_decommission(self, reason=None):
        """FR-IOT-008: stop ingestion, close open alerts and gaps, and mark the
        series terminated. History is kept."""
        _require_role(self.env, IOT_ADMIN, "Decommissioning a stream")
        why = _text(reason)
        if not why:
            raise UserError("Give the reason for decommissioning the stream.")
        for rec in self:
            if rec.state == "decommissioned":
                raise UserError("Stream %s is already decommissioned." % rec.name)
        self._fix_decommission(why)
        return True

    def _fix_decommission(self, why):
        now = fields.Datetime.now()
        uid = self.env.uid
        for rec in self.sudo():
            rec._guarded().write(
                {
                    "state": "decommissioned",
                    "decommissioned_on": now,
                    "decommissioned_by": uid,
                    "decommission_reason": why,
                }
            )
            rec.gap_ids.filtered(lambda g: g.state == "open")._fix_close(now)
            open_alerts = (
                self.env["fix.iot.alert"]
                .sudo()
                .search([("stream_id", "=", rec.id), ("state", "!=", "resolved")])
            )
            for alert in open_alerts:
                alert._guarded().write(
                    {
                        "state": "resolved",
                        "acked_on": alert.acked_on or now,
                        "acked_by": alert.acked_by.id or uid,
                        "resolved_on": now,
                        "resolved_by": uid,
                        "resolution_note": "Closed: stream %s decommissioned (%s)."
                        % (rec.name, why),
                    }
                )
            publish(
                rec.env,
                "telemetry.stream_decommissioned",
                "fix.iot.stream",
                rec.id,
                {
                    "stream": rec.name,
                    "device": rec.device_id.device_id,
                    "metric": rec.metric,
                    "equipment_id": rec.equipment_id.id or False,
                    "site_id": rec.site_id.id or False,
                    "alerts_closed": len(open_alerts),
                    "reason": why,
                },
            )

    def ingest(self, value, timestamp=None):
        reading, alerts = super().ingest(value, timestamp)
        signal = self.sudo().signal_id
        if signal and signal._fix_out_of_range(reading.sudo().value):
            reading.sudo()._guarded().write({"quality_flag": "out_of_range"})
        return reading, alerts


class FixIotTelemetryQuality(models.Model):
    _inherit = "fix.iot.telemetry"

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"quality_flag"}

    quality_flag = fields.Selection(
        [("good", "Good"), ("out_of_range", "Out of Expected Range")],
        string="Quality",
        default="good",
        readonly=True,
        help="FR-IOT-016: a suspect value is kept and flagged, never discarded silently.",
    )


# ---------------------------------------------------------------------------
# Protocol Adapters
# ---------------------------------------------------------------------------
class FixIotAdapterChannels(models.Model):
    _inherit = "fix.iot.adapter"

    protocol = fields.Selection(
        selection_add=[
            ("sparkplug", "MQTT Sparkplug B"),
            ("snmp", "SNMP"),
            ("file", "File Batch"),
            ("aemp", "Telematics (ISO 15143-3 / AEMP 2.0)"),
        ],
        ondelete={
            "sparkplug": "set default",
            "snmp": "set default",
            "file": "set default",
            "aemp": "set default",
        },
    )
    file_batch_ids = fields.One2many("fix.iot.file.batch", "adapter_id", string="File Batches")


_BATCH_TERMS = frozenset({"adapter_id", "batch_file", "batch_filename", "source_ref"})


class FixIotFileBatch(models.Model):
    """FR-IOT-012: a periodic export is a first-class channel. Every row goes
    through the same gates as a live reading (adapter enabled and keyed, stream
    active, consent, duplicates, future dates) and the same rule engine; what
    was refused is reported row by row, never dropped silently (BRU-IOT-08)."""

    _name = "fix.iot.file.batch"
    _description = "IoT File Batch Import"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "processed_by",
            "processed_on",
            "rows_total",
            "rows_accepted",
            "rows_rejected",
            "alerts_raised",
            "report",
        }

    name = fields.Char(required=True, default="New", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    adapter_id = fields.Many2one(
        "fix.iot.adapter", string="Protocol Adapter", required=True, ondelete="restrict", index=True
    )
    source_ref = fields.Char(
        string="Export Reference", help="The sender's file or export reference."
    )
    batch_file = fields.Binary(string="Export File (CSV)", attachment=True, copy=False)
    batch_filename = fields.Char(string="File Name", copy=False)
    state = fields.Selection(
        [("draft", "Draft"), ("processed", "Processed")], required=True, default="draft"
    )
    processed_by = fields.Many2one("res.users", string="Processed By", readonly=True, copy=False)
    processed_on = fields.Datetime(string="Processed On", readonly=True, copy=False)
    rows_total = fields.Integer(string="Rows", readonly=True, copy=False)
    rows_accepted = fields.Integer(string="Accepted", readonly=True, copy=False)
    rows_rejected = fields.Integer(string="Refused", readonly=True, copy=False)
    alerts_raised = fields.Integer(string="Alerts Raised", readonly=True, copy=False)
    report = fields.Text(string="Validation Report", readonly=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        _require_role(self.env, IOT_ADMIN, "Submitting a file batch")
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.iot.file.batch") or "IFBT/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda b: b.state == "processed"):
                if _BATCH_TERMS & set(vals):
                    raise UserError(
                        "File batch %s is processed: it can no longer change." % rec.name
                    )
        return super().write(vals)

    def unlink(self):
        if self.filtered(lambda b: b.state == "processed") and not self.env.su:
            raise AccessError("A processed file batch is ingestion evidence: it is kept.")
        return super().unlink()

    @staticmethod
    def _fix_rows(content):
        text = content.decode("utf-8-sig", errors="replace")
        reader = csv.DictReader(io.StringIO(text))
        header = {(h or "").strip().lower(): h for h in (reader.fieldnames or [])}
        missing = [c for c in ("stream", "timestamp", "value") if c not in header]
        if missing:
            raise UserError(
                "The file needs the columns stream, timestamp and value (missing: %s)."
                % ", ".join(missing)
            )
        rows = []
        for row in reader:
            rows.append({k: _text(row.get(header[k])) for k in ("stream", "timestamp", "value")})
            if len(rows) > MAX_BATCH_ROWS:
                raise UserError(
                    "A file batch holds at most %d rows: split the export." % MAX_BATCH_ROWS
                )
        return rows

    def action_process(self):
        _require_role(self.env, IOT_ADMIN, "Ingesting a file batch")
        Stream = self.env["fix.iot.stream"]
        for rec in self:
            if rec.state != "draft":
                raise UserError("File batch %s is already processed." % rec.name)
            if not rec.batch_file:
                raise UserError("Upload the export file of batch %s first." % rec.name)
            adapter = rec.adapter_id
            rows = self._fix_rows(base64.b64decode(rec.batch_file))
            accepted = refused = alerts = 0
            problems = []
            for number, row in enumerate(rows, start=2):
                stream = Stream.search(
                    [("name", "=", row["stream"]), ("adapter_id", "=", adapter.id)], limit=1
                )
                why = None
                if not stream:
                    why = "stream '%s' is not a stream of adapter %s" % (
                        row["stream"],
                        adapter.name,
                    )
                else:
                    try:
                        stamp = fields.Datetime.to_datetime(row["timestamp"].replace("T", " ")[:19])
                    except ValueError:
                        stamp = None
                    if not stamp:
                        why = "timestamp '%s' is not YYYY-MM-DD HH:MM:SS" % row["timestamp"]
                    else:
                        try:
                            with self.env.cr.savepoint():
                                _reading, raised = stream.ingest(row["value"], stamp)
                            accepted += 1
                            alerts += len(raised)
                        except (IngestRefused, UserError, ValidationError, AccessError) as exc:
                            why = str(exc.args[0] if exc.args else exc)
                if why:
                    refused += 1
                    if len(problems) < 200:
                        problems.append("row %d: %s" % (number, why))
            report = "%d row(s): %d accepted, %d refused, %d alert(s) raised." % (
                len(rows),
                accepted,
                refused,
                alerts,
            )
            if problems:
                report += "\n" + "\n".join(problems)
                if refused > len(problems):
                    report += "\n... and %d more refused row(s)." % (refused - len(problems))
            rec._guarded().write(
                {
                    "state": "processed",
                    "processed_by": self.env.uid,
                    "processed_on": fields.Datetime.now(),
                    "rows_total": len(rows),
                    "rows_accepted": accepted,
                    "rows_rejected": refused,
                    "alerts_raised": alerts,
                    "report": report,
                }
            )
            publish(
                self.env,
                "telemetry.file_batch_ingested",
                "fix.iot.file.batch",
                rec.id,
                {
                    "batch": rec.name,
                    "adapter": adapter.name,
                    "accepted": accepted,
                    "refused": refused,
                },
            )
        refused = sum(self.mapped("rows_rejected"))
        if refused:
            return {"warning": "%d row(s) refused: the validation report says why." % refused}
        return True


# ---------------------------------------------------------------------------
# Threshold Alerting
# ---------------------------------------------------------------------------
_WINDOW_TERMS = frozenset({"device_id", "site_id", "date_from", "date_to", "reason"})


class FixIotMaintenanceWindow(models.Model):
    """FR-IOT-032 / BRU-IOT-16 / §8.3 Suppressed: planned work on an asset
    would raise alerts nobody needs. A window names the device or site, a
    bounded period and the reason; an IoT Manager other than the requester
    approves it. While it runs, rule breaches on that asset raise no alert and
    are counted on the window."""

    _name = "fix.iot.maintenance.window"
    _description = "IoT Maintenance Window"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "date_from desc, id desc"

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "requested_by",
            "requested_on",
            "approved_by",
            "approved_on",
            "cancelled_by",
            "cancel_reason",
            "suppressed_count",
        }

    name = fields.Char(required=True, default="New", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    device_id = fields.Many2one("fix.iot.device", string="Device", ondelete="cascade", index=True)
    site_id = fields.Many2one("fix.site", string="Site (every device on it)", ondelete="cascade")
    date_from = fields.Datetime(string="From", required=True)
    date_to = fields.Datetime(string="Until", required=True)
    reason = fields.Char(required=True, string="Planned Work")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("requested", "Awaiting Approval"),
            ("approved", "Approved"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="draft",
        tracking=True,
    )
    requested_by = fields.Many2one("res.users", string="Requested By", readonly=True, copy=False)
    requested_on = fields.Datetime(string="Requested On", readonly=True, copy=False)
    approved_by = fields.Many2one("res.users", string="Approved By", readonly=True, copy=False)
    approved_on = fields.Datetime(string="Approved On", readonly=True, copy=False)
    cancelled_by = fields.Many2one("res.users", string="Cancelled By", readonly=True, copy=False)
    cancel_reason = fields.Char(string="Why Cancelled", readonly=True, copy=False)
    suppressed_count = fields.Integer(string="Breaches Suppressed", readonly=True, copy=False)

    @api.constrains("device_id", "site_id", "date_from")
    def _check_subject(self):
        for rec in self:
            if bool(rec.device_id) == bool(rec.site_id):
                raise ValidationError(
                    "A maintenance window covers one device or one site: name exactly one."
                )

    @api.constrains("date_from", "date_to")
    def _check_period(self):
        for rec in self:
            if rec.date_to <= rec.date_from:
                raise ValidationError("A maintenance window ends after it starts.")
            if rec.date_to - rec.date_from > timedelta(days=MAX_WINDOW_DAYS):
                raise ValidationError(
                    "A maintenance window lasts at most %d days: indefinite suppression is "
                    "not permitted (BRU-IOT-16)." % MAX_WINDOW_DAYS
                )

    @api.model_create_multi
    def create(self, vals_list):
        _require_role(self.env, IOT_OPERATOR, "Planning a maintenance window")
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.iot.maintenance.window") or "IMWN/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda w: w.state != "draft"):
                changed = [
                    n
                    for n in _WINDOW_TERMS & set(vals)
                    if rec._fix_guard_differs(n, vals[n], rec[n])
                ]
                if changed:
                    raise UserError(
                        "Maintenance window %s is %s: its terms can no longer change. Cancel it "
                        "and plan a new one." % (rec.name, rec.state)
                    )
        return super().write(vals)

    def action_request(self):
        _require_role(self.env, IOT_OPERATOR, "Requesting a maintenance window")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Request approval of a draft window.")
            if rec.date_to <= fields.Datetime.now():
                raise UserError("Window %s has already ended." % rec.name)
            rec._guarded().write(
                {
                    "state": "requested",
                    "requested_by": self.env.uid,
                    "requested_on": fields.Datetime.now(),
                }
            )
        return True

    def action_approve(self):
        _require_role(self.env, IOT_MANAGER, "Approving a maintenance window")
        for rec in self:
            if rec.state != "requested":
                raise UserError("Approve a window awaiting approval.")
            if not self.env.su and self.env.user in (rec.requested_by | rec.create_uid):
                raise UserError(
                    "The requester of window %s cannot approve it: suppression needs a named "
                    "approver other than the requester (BRU-IOT-16)." % rec.name
                )
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by": self.env.uid,
                    "approved_on": fields.Datetime.now(),
                }
            )
        return True

    def action_cancel(self, reason=None):
        _require_role(self.env, IOT_OPERATOR, "Cancelling a maintenance window")
        why = _text(reason)
        if not why:
            raise UserError("Give the reason for cancelling the window.")
        for rec in self:
            if rec.state == "cancelled":
                raise UserError("Window %s is already cancelled." % rec.name)
            rec._guarded().write(
                {"state": "cancelled", "cancelled_by": self.env.uid, "cancel_reason": why}
            )
        return True

    @api.model
    def _fix_active_for(self, device, ts):
        domain = [
            ("state", "=", "approved"),
            ("date_from", "<=", ts),
            ("date_to", ">=", ts),
            "|",
            ("device_id", "=", device.id),
            ("site_id", "=", device.site_id.id or -1),
        ]
        return self.sudo().search(domain, limit=1)


class FixIotRuleWindow(models.Model):
    _inherit = "fix.iot.rule"

    def _fix_evaluate(self, stream, value, ts):
        window = self.env["fix.iot.maintenance.window"]._fix_active_for(stream.device_id, ts)
        if window:
            breaching = self.sudo().filtered(lambda r: r.matches(value))
            if breaching:
                window._guarded().write(
                    {"suppressed_count": window.suppressed_count + len(breaching)}
                )
            return self.env["fix.iot.alert"].sudo().browse()
        return super()._fix_evaluate(stream, value, ts)


# ---------------------------------------------------------------------------
# Failure Prediction
# ---------------------------------------------------------------------------
_DIRECT_OUTCOMES = {
    "confirmed": "the predicted failure occurred",
    "false_alarm": "the horizon passed with no failure",
    "unknown": "the outcome cannot be established",
}


class FixPredictionCapture(models.Model):
    _inherit = "fix.predictive.maintenance"

    _OUTPUT_FIELDS = {
        "equipment_id",
        "prediction",
        "confidence",
        "estimated_days_to_failure",
        "model_name",
        "feature_window_from",
        "feature_window_to",
        "last_evaluated",
        "failure_mode",
        "rul_low_days",
        "rul_high_days",
    }

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"outcome_evidence_ref"}

    failure_mode = fields.Char(
        string="Predicted Failure Mode",
        help="What the model says will fail, e.g. bearing wear, SMART reallocation.",
    )
    rul_low_days = fields.Integer(string="RUL Low (days)")
    rul_high_days = fields.Integer(string="RUL High (days)")
    outcome = fields.Selection(
        selection_add=[("unknown", "Unknown (excluded from precision)")],
        ondelete={"unknown": "set default"},
    )
    outcome_evidence_ref = fields.Char(string="Outcome Evidence", readonly=True, copy=False)
    horizon_end = fields.Date(compute="_compute_horizon_end", string="Horizon Ends")

    @api.constrains("rul_low_days", "rul_high_days", "estimated_days_to_failure")
    def _check_rul_interval(self):
        for rec in self:
            low, high, days = (
                rec.rul_low_days or 0,
                rec.rul_high_days or 0,
                rec.estimated_days_to_failure or 0,
            )
            if low < 0 or high < 0:
                raise ValidationError("A remaining-useful-life bound cannot be negative.")
            if (low or high) and not (low <= days <= high):
                raise ValidationError(
                    "The remaining useful life is an interval around the estimate: the low "
                    "bound, days to failure and the high bound must be in that order (FR-IOT-041)."
                )

    def _compute_horizon_end(self):
        for rec in self:
            base = rec.last_evaluated or rec.create_date
            rec.horizon_end = (
                (base + timedelta(days=max(rec.estimated_days_to_failure or 0, 1))).date()
                if base
                else False
            )

    def action_record_outcome(self, outcome=None, note=None, evidence_ref=None):
        """FR-IOT-044 / BRU-IOT-14 / AUT-IOT-16: every prediction gets an
        outcome. An intervention records its finding when it completes; this
        records it for a prediction no intervention acted on. A false alarm or
        an unknown outcome waits for the horizon; a confirmed failure needs
        evidence. Whoever recorded the score does not mark it right."""
        _require_role(self.env, IOT_OPERATOR, "Recording a prediction outcome")
        if outcome not in _DIRECT_OUTCOMES:
            raise UserError(
                "Choose the outcome: Failure Confirmed, False Alarm or Unknown (excluded from "
                "precision)."
            )
        why = _text(note)
        if not why:
            raise UserError("Describe how the outcome was established.")
        evidence = _text(evidence_ref)
        today = fields.Date.context_today(self)
        for rec in self:
            pred = rec.sudo()
            if pred.prediction == "healthy":
                raise UserError(
                    "Prediction %s predicts a healthy asset: there is no failure to confirm."
                    % pred.name
                )
            if pred.outcome != "pending":
                raise UserError("Prediction %s already has its outcome." % pred.name)
            busy = pred.action_ids.filtered(
                lambda a: a.state in ("approved", "dispatched") or a.approval_state == "pending"
            )
            if busy:
                raise UserError(
                    "Prediction %s has action %s under way: its completion records the outcome."
                    % (pred.name, busy[0].name)
                )
            if not self.env.su and pred.create_uid == self.env.user:
                raise UserError(
                    "You recorded prediction %s: someone else records whether it came true."
                    % pred.name
                )
            if outcome == "confirmed" and not evidence:
                raise UserError(
                    "A confirmed failure needs its evidence: the job card, fault report or "
                    "service order that shows it."
                )
            if outcome != "confirmed" and pred.horizon_end and today < pred.horizon_end:
                raise UserError(
                    "Prediction %s looks %s days ahead: whether it was a false alarm is known "
                    "from %s." % (pred.name, pred.estimated_days_to_failure, pred.horizon_end)
                )
            rec._guarded().write(
                {
                    "outcome": outcome,
                    "outcome_note": why,
                    "outcome_evidence_ref": evidence or False,
                    "outcome_recorded_by": self.env.uid,
                    "outcome_recorded_on": fields.Datetime.now(),
                }
            )
            publish(
                self.env,
                "intervention.outcome_recorded",
                "fix.predictive.maintenance",
                rec.id,
                {
                    "prediction": pred.name,
                    "model": pred.model_name or "",
                    "outcome": outcome,
                    "intervention_performed": False,
                    "evidence_ref": evidence,
                },
            )
        return True


# ---------------------------------------------------------------------------
# Prescriptive Routing
# ---------------------------------------------------------------------------
class FixIotActionPart(models.Model):
    """FR-IOT-042: the parts an intervention likely needs, checked against
    stock (M15). Fixed once the action leaves proposed: the approval covered
    them."""

    _name = "fix.iot.action.part"
    _description = "Prescriptive Action Part"
    _order = "id"

    action_id = fields.Many2one("fix.iot.action", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="action_id.company_id", store=True, string="Company")
    product_id = fields.Many2one(
        "product.product", string="Part", required=True, ondelete="restrict"
    )
    quantity = fields.Float(required=True, default=1.0)
    on_hand = fields.Float(compute="_compute_availability", string="On Hand")
    availability = fields.Selection(
        [("available", "Available"), ("short", "Short"), ("unknown", "Not Stocked")],
        compute="_compute_availability",
    )

    _quantity_positive = models.Constraint("CHECK (quantity > 0)", "A part quantity is positive.")

    def _compute_availability(self):
        Quant = self.env["stock.quant"].sudo() if "stock.quant" in self.env else None
        for rec in self:
            if Quant is None or not rec.product_id:
                rec.on_hand, rec.availability = 0.0, "unknown"
                continue
            domain = [
                ("product_id", "=", rec.product_id.id),
                ("location_id.usage", "=", "internal"),
            ]
            if rec.company_id:
                domain.append(("company_id", "in", [rec.company_id.id, False]))
            quants = Quant.search(domain)
            free = sum(q.quantity - q.reserved_quantity for q in quants)
            rec.on_hand = free
            if not quants:
                rec.availability = "unknown"
            else:
                rec.availability = "available" if free >= rec.quantity else "short"

    def _fix_check_open(self, actions):
        if self.env.su:
            return
        for action in actions:
            if action.state != "proposed":
                raise UserError(
                    "Action %s is %s: its parts were part of what was approved. Use Revise Terms "
                    "to change them." % (action.name, action.state)
                )

    @api.model_create_multi
    def create(self, vals_list):
        self._fix_check_open(
            self.env["fix.iot.action"].browse([v.get("action_id") for v in vals_list])
        )
        return super().create(vals_list)

    def write(self, vals):
        self._fix_check_open(self.action_id)
        return super().write(vals)

    def unlink(self):
        self._fix_check_open(self.action_id)
        return super().unlink()


class FixIotActionCapture(models.Model):
    _inherit = "fix.iot.action"

    part_ids = fields.One2many("fix.iot.action.part", "action_id", string="Parts Likely Needed")
    skill_code = fields.Char(
        string="Skill Required (M22)", help="The code of the M22 competency the technician needs."
    )
    skill_name = fields.Char(compute="_compute_skill_name", string="Skill")
    parts_state = fields.Selection(
        [
            ("none", "No Parts"),
            ("available", "All Available"),
            ("short", "Shortage"),
            ("unknown", "Not Stocked"),
        ],
        compute="_compute_parts_state",
        string="Parts",
    )
    recommended_action = fields.Text(string="Recommended Action")

    def _fix_competency(self):
        self.ensure_one()
        if "fix.competency" not in self.env or not _text(self.skill_code):
            return None
        return (
            self.env["fix.competency"]
            .sudo()
            .search([("code", "=", _text(self.skill_code))], limit=1)
            or None
        )

    def _compute_skill_name(self):
        for rec in self:
            comp = rec._fix_competency()
            rec.skill_name = comp.name if comp else False

    @api.depends("part_ids.quantity", "part_ids.product_id")
    def _compute_parts_state(self):
        for rec in self:
            states = set(rec.part_ids.mapped("availability"))
            if not rec.part_ids:
                rec.parts_state = "none"
            elif "short" in states:
                rec.parts_state = "short"
            elif "unknown" in states:
                rec.parts_state = "unknown"
            else:
                rec.parts_state = "available"

    @api.constrains("skill_code")
    def _check_skill(self):
        if "fix.competency" not in self.env:
            return
        for rec in self:
            if _text(rec.skill_code) and not rec._fix_competency():
                raise ValidationError(
                    "Skill %s is not an M22 competency code." % _text(rec.skill_code)
                )

    def write(self, vals):
        if self and not self._fix_guard_open() and "skill_code" in vals:
            for rec in self.filtered(lambda a: a.state != "proposed"):
                if rec._fix_guard_differs("skill_code", vals["skill_code"], rec.skill_code):
                    raise UserError(
                        "Action %s is %s: the skill was part of what was approved. Use Revise "
                        "Terms to change it." % (rec.name, rec.state)
                    )
        return super().write(vals)

    def action_request_approval(self, justification=None):
        """Spec §12.3 intervention.proposed: the proposal goes to its approver
        with the parts it needs (and whether stock has them) and the skill."""
        res = super().action_request_approval(justification=justification)
        for rec in self:
            publish(
                rec.env,
                "intervention.proposed",
                "fix.iot.action",
                rec.id,
                {
                    "action": rec.name,
                    "prediction": rec.prediction_id.sudo().name,
                    "equipment_id": rec.equipment_id.id or False,
                    "action_type": rec.action_type,
                    "skill": _text(rec.skill_code),
                    "parts": [
                        {
                            "product_id": p.product_id.id,
                            "quantity": p.quantity,
                            "availability": p.availability,
                        }
                        for p in rec.part_ids
                    ],
                    # M45 equipment is the company's own: no M08 entitlement or M07 route.
                    "commercial_route": "internal",
                },
            )
        return res
