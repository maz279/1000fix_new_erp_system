# fix_msp — M05: MSP contracts, alerts, sessions, service reports (P08-M07).
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish


class FixMspContract(models.Model):
    """The MSP service model ON M08's contract engine (never beside it)."""
    _name = "fix.msp.contract"
    _description = "MSP Contract"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    name = fields.Char(required=True)
    contract_id = fields.Many2one("fix.contract", string="Contract (M08)",
                                  required=True, ondelete="cascade")
    device_count = fields.Integer(string="Covered Devices")
    monitoring_scope = fields.Selection(
        [("endpoints", "Endpoints Only"), ("endpoints_network", "Endpoints + Network"),
         ("full", "Full Stack")], default="endpoints", required=True)
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    per_device_monthly = fields.Monetary(string="Per-Device Monthly",
                                         currency_field="currency_id")
    asset_ids = fields.One2many("fix.monitored.asset", "msp_contract_id",
                                string="Monitored Assets")
    report_ids = fields.One2many("fix.msp.service.report", "msp_contract_id",
                                 string="Service Reports")

    @api.depends("asset_ids")
    def _compute_asset_count(self):
        for rec in self:
            rec.device_count = len(rec.asset_ids)

    def action_monthly_report(self, period):
        """Journey 6's ending: the client-facing monthly report."""
        self.ensure_one()
        alerts = self.env["fix.msp.alert"].search([
            ("msp_contract_id", "=", self.id),
            ("create_date", ">=", period[0]),
            ("create_date", "<=", period[1])])
        resolved = alerts.filtered(lambda a: a.state == "resolved")
        report = self.env["fix.msp.service.report"].create({
            "msp_contract_id": self.id,
            "period_label": period[2],
            "alert_count": len(alerts),
            "resolved_count": len(resolved),
            "sla_attainment": round(
                (len(resolved) / len(alerts)) if alerts else 1.0, 4),
        })
        publish(self.env, "msp.service_report_published",
                "fix.msp.service.report", report.id,
                {"contract": self.name, "period": period[2]})
        return report


    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
class FixMonitoredAsset(models.Model):
    """A client endpoint under management (fed by rmm-collector)."""
    _name = "fix.monitored.asset"
    _description = "Monitored Asset"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    msp_contract_id = fields.Many2one("fix.msp.contract", required=True,
                                      ondelete="cascade", index=True)
    agent_id = fields.Char(required=True, help="RMM agent identifier")
    hostname = fields.Char()
    last_seen = fields.Datetime(readonly=True)
    health = fields.Selection([("healthy", "Healthy"), ("degraded", "Degraded"),
                               ("offline", "Offline")],
                              default="healthy", required=True)

    @api.model
    def ingest_telemetry(self, agent_id, health, seen_at):
        """The collector's ingestion path (INT-029): last_seen and health
        update; the FIRST unhealthy transition raises an ALERT."""
        asset = self.search([("agent_id", "=", agent_id)], limit=1)
        if not asset:
            raise UserError("Unknown RMM agent %s" % agent_id)
        became_unhealthy = health != "healthy" and asset.health == "healthy"
        asset.write({"health": health, "last_seen": seen_at})
        if became_unhealthy:
            alert = self.env["fix.msp.alert"].create({
                "msp_contract_id": asset.msp_contract_id.id,
                "asset_id": asset.id,
                "severity": "major" if health == "offline" else "minor",
                "message": "%s became %s" % (asset.hostname or agent_id, health),
            })
            publish(self.env, "msp.alert_raised", "fix.msp.alert", alert.id,
                    {"agent": agent_id, "health": health})


    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
class FixMspAlert(models.Model):
    """An alert from the RMM collector; ticketing is a service order."""
    _name = "fix.msp.alert"
    _description = "MSP Alert"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    msp_contract_id = fields.Many2one("fix.msp.contract", required=True,
                                      index=True)
    asset_id = fields.Many2one("fix.monitored.asset", required=True)
    severity = fields.Selection([("minor", "Minor"), ("major", "Major")],
                                default="minor", required=True)
    message = fields.Char(required=True)
    state = fields.Selection([("new", "New"), ("acked", "Acknowledged"),
                              ("ticketed", "Ticketed"),
                              ("resolved", "Resolved")],
                             default="new", required=True, tracking=True)
    order_id = fields.Many2one("fix.service.order", string="Service Order",
                               ondelete="set null")

    def action_acknowledge(self):
        for rec in self:
            if rec.state != "new":
                raise UserError("Only NEW alerts acknowledge")
            rec.state = "acked"

    def action_to_ticket(self):
        """Journey 6: alert -> ticket. The ticket IS a service order with
        the MSP contract's customer; SLA flows from M08's terms."""
        for rec in self:
            if rec.state not in ("new", "acked"):
                raise UserError("Alert already ticketed or resolved")
            order = self.env["fix.service.order"].create({
                "customer_id": rec.msp_contract_id.contract_id.customer_id.id
                if rec.msp_contract_id.contract_id.customer_id else False,
                "branch_id": False,
                "fault_description": "MSP alert: %s" % rec.message,
                "order_category": "amc",
            })
            rec.write({"state": "ticketed", "order_id": order.id})
            publish(self.env, "msp.alert_ticketed", "fix.msp.alert", rec.id,
                    {"order": order.name})


    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
class FixRemoteSession(models.Model):
    """A remote support session (INT-028 MeshCentral/RustDesk) with PDPA
    consent capture — the session is lawful, or it does not start."""
    _name = "fix.remote.session"
    _description = "Remote Session"
    # P03 workspace data-entry form (discovered by cd_p03_portal).
    _p03_capture = {
        "module": "M05",
        "form": "Remote Session (consent recorded)",
        "fields": ["msp_contract_id", "asset_id", "technician_id", "tool",
                   "consent_captured", "started_at"],
    }
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "started_at desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    msp_contract_id = fields.Many2one("fix.msp.contract", required=True)
    asset_id = fields.Many2one("fix.monitored.asset", required=True)
    technician_id = fields.Many2one("hr.employee", string="Technician",
                                    required=True)
    tool = fields.Selection([("meshcentral", "MeshCentral"),
                             ("rustdesk", "RustDesk")],
                            default="meshcentral", required=True)
    consent_captured = fields.Boolean(
        required=True, default=False,
        help="PDPA: the client user's consent to the remote session - "
             "without it the session does not start")
    started_at = fields.Datetime(default=fields.Datetime.now, required=True)
    ended_at = fields.Datetime(readonly=True)

    def action_start(self):
        for rec in self:
            if not rec.consent_captured:
                raise UserError(
                    "PDPA: remote sessions require captured consent - "
                    "this one did not start")
            publish(self.env, "msp.remote_session_started",
                    "fix.remote.session", rec.id,
                    {"asset": rec.asset_id.hostname or rec.asset_id.agent_id})

    def action_end(self):
        for rec in self:
            rec.ended_at = fields.Datetime.now()
            publish(self.env, "msp.remote_session_ended",
                    "fix.remote.session", rec.id, {})


    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
class FixMspServiceReport(models.Model):
    """The monthly client-facing service report (bilingual fields, DE-17)."""
    _name = "fix.msp.service.report"
    _description = "MSP Service Report"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    msp_contract_id = fields.Many2one("fix.msp.contract", required=True,
                                      ondelete="cascade")
    period_label = fields.Char(string="Period", required=True)
    alert_count = fields.Integer()
    resolved_count = fields.Integer()
    sla_attainment = fields.Float(string="SLA Attainment (0-1)")
    summary_bn = fields.Text(string="সারসংক্ষেপ (Bengali)", help="DE-17")
    summary_en = fields.Text(string="Summary (English)")

    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")