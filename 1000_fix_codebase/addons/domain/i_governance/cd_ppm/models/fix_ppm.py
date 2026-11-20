# fix_ppm — M67: project, program, portfolio management (P10-M05).
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish


class FixProject(models.Model):
    _name = "fix.project"
    _description = "Project"
    # P03 workspace data-entry form (discovered by cd_p03_portal).
    _p03_capture = {
        "module": "M67",
        "form": "Project (6 types)",
        "fields": ["name", "project_type", "manager_id", "date_start", "date_end", "budget"],
    }
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_start desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    code = fields.Char(string="Project Code", readonly=True, copy=False)
    project_type = fields.Selection(
        [("internal", "Internal"), ("client", "Client Project"),
         ("infrastructure", "Infrastructure")],
        required=True, default="internal")
    manager_id = fields.Many2one("hr.employee", string="Project Manager")
    date_start = fields.Date()
    date_end = fields.Date()
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    budget = fields.Monetary(string="Budget", currency_field="currency_id")
    actual_cost = fields.Monetary(string="Actual Cost",
                                   currency_field="currency_id")
    progress_pct = fields.Float(string="Progress %", default=0.0)
    state = fields.Selection([("draft", "Draft"), ("active", "Active"),
                              ("on_hold", "On Hold"),
                              ("completed", "Completed"),
                              ("cancelled", "Cancelled")],
                              default="draft", required=True, tracking=True)
    milestone_ids = fields.One2many("fix.project.milestone", "project_id",
                                     string="Milestones")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["code"] = self.env["ir.sequence"].next_by_code(
                "fix.project") or "PRJ/New"
        recs = super().create(vals_list)
        for rec in recs:
            publish(self.env, "project.created", "fix.project", rec.id,
                    {"name": rec.name, "type": rec.project_type})
        return recs

    def action_complete(self):
        """A project with open milestones does NOT complete."""
        for rec in self:
            open_ms = rec.milestone_ids.filtered(lambda m: m.state != "done")
            if open_ms:
                raise UserError(
                    "%d milestone(s) still open" % len(open_ms))
            rec.state = "completed"
            publish(self.env, "project.completed", "fix.project", rec.id,
                    {"name": rec.name})


class FixProjectMilestone(models.Model):
    _name = "fix.project.milestone"
    _description = "Project Milestone"
    # P03 workspace data-entry form (discovered by cd_p03_portal).
    _p03_capture = {
        "module": "M67",
        "form": "Milestone",
        "fields": ["name", "project_id", "due_date"],
    }
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    project_id = fields.Many2one("fix.project", required=True,
                                  ondelete="cascade")
    due_date = fields.Date()
    state = fields.Selection([("pending", "Pending"), ("done", "Done")],
                              default="pending", required=True, tracking=True)
