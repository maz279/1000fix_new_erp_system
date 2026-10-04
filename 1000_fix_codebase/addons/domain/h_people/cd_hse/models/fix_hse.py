# fix_hse — M59: HSE incidents + Labour Rules safety (P09-M08).
from odoo import api, fields, models

from libs.py.fix_events import publish


class FixHseIncident(models.Model):
    _name = "fix.hse.incident"
    _description = "HSE Incident"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, copy=False, readonly=True,
                       default=lambda self: "New")
    incident_type = fields.Selection(
        [("injury", "Injury"), ("near_miss", "Near Miss"),
         ("property_damage", "Property Damage"), ("fire", "Fire"),
         ("environmental", "Environmental Spill")],
        required=True, default="near_miss")
    severity = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        default="low", required=True, tracking=True)
    branch_id = fields.Many2one("fix.branch", string="Branch")
    employee_id = fields.Many2one("hr.employee", string="Reported By")
    description = fields.Text(required=True)
    corrective_action = fields.Text()
    state = fields.Selection(
        [("reported", "Reported"), ("investigating", "Investigating"),
         ("action_taken", "Action Taken"), ("closed", "Closed")],
        default="reported", required=True, tracking=True)
    reported_at = fields.Datetime(default=fields.Datetime.now, readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "fix.hse.incident") or "HSE/New"
        recs = super().create(vals_list)
        for rec in recs:
            publish(self.env, "hse.incident_reported", "fix.hse.incident",
                    rec.id, {"type": rec.incident_type})
        return recs


class FixSafetyInspection(models.Model):
    _name = "fix.safety.inspection"
    _description = "Safety Inspection"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    branch_id = fields.Many2one("fix.branch", string="Branch", required=True)
    inspected_on = fields.Date(required=True, default=fields.Date.today)
    inspector_id = fields.Many2one("hr.employee", string="Inspector")
    fire_extinguisher_ok = fields.Boolean(default=True)
    emergency_exit_ok = fields.Boolean(default=True)
    first_aid_ok = fields.Boolean(default=True)
    electrical_ok = fields.Boolean(default=True)
    findings = fields.Text()
    state = fields.Selection([("scheduled", "Scheduled"), ("done", "Done"),
                              ("follow_up", "Follow-up Required")],
                             default="scheduled", required=True, tracking=True)

    def action_complete(self):
        for rec in self:
            needs = not all([rec.fire_extinguisher_ok, rec.emergency_exit_ok,
                             rec.first_aid_ok, rec.electrical_ok])
            rec.state = "follow_up" if needs else "done"
