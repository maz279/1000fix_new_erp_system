# fix_talent — M58: talent acquisition and onboarding (P09-M08).
from odoo import api, fields, models

from libs.py.fix_events import publish


class FixJobRequisition(models.Model):
    """M58: talent acquisition. The joiner event drives M29 provisioning."""
    _name = "fix.job.requisition"
    _description = "Job Requisition"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    department_id = fields.Many2one("hr.department", string="Department")
    position_id = fields.Many2one("fix.org.position", string="Position")
    openings = fields.Integer(default=1, required=True)
    state = fields.Selection([("draft", "Draft"), ("open", "Open"),
                              ("hired", "Hired"), ("closed", "Closed")],
                             default="draft", required=True, tracking=True)

    def action_open(self):
        for rec in self:
            rec.state = "open"

    def action_hired(self):
        for rec in self:
            rec.state = "hired"
            publish(self.env, "employee.hired", "fix.job.requisition",
                    rec.id, {"position": rec.position_id.name or rec.name})


class FixCandidate(models.Model):
    _name = "fix.candidate"
    _description = "Candidate"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    email = fields.Char()
    phone = fields.Char()
    requisition_id = fields.Many2one("fix.job.requisition", string="Requisition")
    state = fields.Selection(
        [("applied", "Applied"), ("screening", "Screening"),
         ("interview", "Interview"), ("offered", "Offered"),
         ("hired", "Hired"), ("rejected", "Rejected")],
        default="applied", required=True, tracking=True)
