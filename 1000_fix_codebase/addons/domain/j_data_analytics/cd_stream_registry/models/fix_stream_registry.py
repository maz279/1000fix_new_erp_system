# fix_stream_registry — M48: IoT telemetry, alerting, PdM (P11-M03).
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish


class FixIotDevice(models.Model):
    """M48: IoT device registry on M17's asset registry."""

    _name = "fix.iot.device"
    _description = "IoT Device"
    _inherit = ["mail.thread", "mail.activity.mixin"]

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
    last_telemetry = fields.Datetime(readonly=True)
    status = fields.Selection(
        [("online", "Online"), ("degraded", "Degraded"), ("offline", "Offline")],
        default="online",
        required=True,
        tracking=True,
    )
    alert_ids = fields.One2many("fix.iot.alert", "device_id", string="Alerts")

    def action_telemetry_received(self, health):
        """Update on telemetry; unhealthy transitions raise alerts."""
        for rec in self:
            became_unhealthy = health != "online" and rec.status == "online"
            rec.write({"status": health, "last_telemetry": fields.Datetime.now()})
            if became_unhealthy:
                alert = self.env["fix.iot.alert"].create(
                    {
                        "device_id": rec.id,
                        "severity": "major" if health == "offline" else "minor",
                        "message": f"{rec.name} became {health}",
                    }
                )
                # The aggregate is the ALERT (it was published with the
                # device's id under the fix.iot.alert aggregate).
                publish(
                    self.env,
                    "iot.alert_raised",
                    "fix.iot.alert",
                    alert.id,
                    {"device": rec.device_id, "health": health},
                )


class FixIotTelemetry(models.Model):
    """M48: telemetry record (time-series; the volume model at 50k/min)."""

    _name = "fix.iot.telemetry"
    _description = "IoT Telemetry"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "timestamp desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    device_id = fields.Many2one("fix.iot.device", required=True, ondelete="cascade", index=True)
    timestamp = fields.Datetime(required=True, default=fields.Datetime.now, index=True)
    metric = fields.Char(required=True, help="e.g. temperature, vibration, gps_lat")
    value = fields.Float(required=True)
    unit = fields.Char(help="e.g. C, mm/s, deg")


class FixIotAlert(models.Model):
    """M48: IoT alerting with threshold configuration."""

    _name = "fix.iot.alert"
    _description = "IoT Alert"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

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
    resolved_on = fields.Datetime(string="Resolved On", readonly=True)
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
        for rec in self:
            if rec.state != "new":
                raise UserError("Acknowledge a new alert")
            rec.write({"state": "acked", "acked_on": fields.Datetime.now()})

    def action_resolve(self):
        for rec in self:
            if rec.state == "resolved":
                raise UserError("Alert is already resolved")
            rec.write({"state": "resolved", "resolved_on": fields.Datetime.now()})


class FixPredictiveMaintenance(models.Model):
    """M48: predictive-maintenance model wired to M26's ML gateway.
    Predicted failures become preventive work orders through M02 dispatch."""

    _name = "fix.predictive.maintenance"
    _description = "Predictive Maintenance Prediction"
    _inherit = ["mail.thread", "mail.activity.mixin"]

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
    model_name = fields.Char(string="Model", help="The M26 model that produced this score")
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
    work_order_created = fields.Boolean(default=False, readonly=True)
    action_ids = fields.One2many("fix.iot.action", "prediction_id", string="Prescriptive Actions")

    def action_create_preventive_wo(self):
        """Wire predicted failures into M02 dispatch as preventive work."""
        for rec in self:
            if rec.prediction != "failure_predicted":
                raise UserError("Only failure predictions create preventive work orders")
            if rec.work_order_created:
                raise UserError("Work order already created for this prediction")
            rec.work_order_created = True
            publish(
                self.env,
                "predictive_maintenance.wo_created",
                "fix.predictive.maintenance",
                rec.id,
                {"equipment": rec.equipment_id.name, "days": rec.estimated_days_to_failure},
            )
