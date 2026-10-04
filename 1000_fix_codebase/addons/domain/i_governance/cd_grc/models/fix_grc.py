# fix_grc — M60: governance, risk, compliance (P09-M08).
from odoo import api, fields, models

from libs.py.fix_events import publish


class FixRiskRegister(models.Model):
    _name = "fix.risk.register"
    _description = "Risk Register Entry"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    category = fields.Selection(
        [("strategic", "Strategic"), ("operational", "Operational"),
         ("financial", "Financial"), ("compliance", "Compliance"),
         ("cyber", "Cyber Security")], required=True, default="operational")
    likelihood = fields.Selection(
        [("1", "Rare"), ("2", "Unlikely"), ("3", "Possible"),
         ("4", "Likely"), ("5", "Almost Certain")], default="3")
    impact = fields.Selection(
        [("1", "Insignificant"), ("2", "Minor"), ("3", "Moderate"),
         ("4", "Major"), ("5", "Severe")], default="3")
    risk_score = fields.Integer(compute="_compute_score", store=True)
    mitigation = fields.Text()
    owner_id = fields.Many2one("hr.employee", string="Risk Owner")
    state = fields.Selection([("open", "Open"), ("mitigating", "Mitigating"),
                              ("closed", "Closed")],
                             default="open", required=True, tracking=True)

    @api.depends("likelihood", "impact")
    def _compute_score(self):
        for rec in self:
            rec.risk_score = int(rec.likelihood or "3") * int(rec.impact or "3")


class FixControl(models.Model):
    _name = "fix.control"
    _description = "Control"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    control_type = fields.Selection(
        [("preventive", "Preventive"), ("detective", "Detective"),
         ("corrective", "Corrective")], required=True, default="preventive")
    frequency = fields.Selection(
        [("continuous", "Continuous"), ("daily", "Daily"),
         ("weekly", "Weekly"), ("monthly", "Monthly"), ("annual", "Annual")],
        default="continuous", required=True)
    risk_id = fields.Many2one("fix.risk.register", string="Risk Addressed")
    last_tested = fields.Date()
    test_result = fields.Selection(
        [("effective", "Effective"), ("partially", "Partially Effective"),
         ("ineffective", "Ineffective")])
    state = fields.Selection([("active", "Active"), ("inactive", "Inactive")],
                             default="active", required=True)
