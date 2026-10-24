# fix_ppm — M67: project, program, portfolio management (P10-M05 / R08-M03).
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish


class FixProject(models.Model):
    _name = "fix.project"
    _description = "Project"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_start desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    code = fields.Char(string="Project Code", readonly=True, copy=False)
    project_type = fields.Selection(
        [
            ("internal", "Internal"),
            ("client", "Client Project"),
            ("infrastructure", "Infrastructure"),
        ],
        required=True,
        default="internal",
    )
    manager_id = fields.Many2one("hr.employee", string="Project Manager")
    date_start = fields.Date()
    date_end = fields.Date()
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    budget = fields.Monetary(string="Budget", currency_field="currency_id")
    actual_cost = fields.Monetary(string="Actual Cost", currency_field="currency_id")
    budget_variance = fields.Monetary(
        compute="_compute_variance",
        string="Budget Variance",
        currency_field="currency_id",
        store=True,
    )
    variance_pct = fields.Float(compute="_compute_variance", string="Variance %", store=True)
    progress_pct = fields.Float(string="Progress %", default=0.0)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("on_hold", "On Hold"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    milestone_ids = fields.One2many("fix.project.milestone", "project_id", string="Milestones")
    task_ids = fields.One2many("fix.project.task", "project_id", string="Tasks")

    @api.depends("budget", "actual_cost")
    def _compute_variance(self):
        for rec in self:
            rec.budget_variance = (rec.budget or 0.0) - (rec.actual_cost or 0.0)
            rec.variance_pct = ((rec.budget_variance / rec.budget) * 100.0) if rec.budget else 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["code"] = self.env["ir.sequence"].next_by_code("fix.project") or "PRJ/New"
        recs = super().create(vals_list)
        for rec in recs:
            publish(
                self.env,
                "project.created",
                "fix.project",
                rec.id,
                {"name": rec.name, "type": rec.project_type},
            )
        return recs

    def action_activate(self):
        for rec in self:
            rec.state = "active"

    def action_complete(self):
        """A project with open milestones does NOT complete."""
        for rec in self:
            open_ms = rec.milestone_ids.filtered(lambda m: m.state != "done")
            if open_ms:
                raise UserError("%d milestone(s) still open" % len(open_ms))
            rec.state = "completed"
            publish(self.env, "project.completed", "fix.project", rec.id, {"name": rec.name})


class FixProjectMilestone(models.Model):
    _name = "fix.project.milestone"
    _description = "Project Milestone"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    project_id = fields.Many2one("fix.project", required=True, ondelete="cascade")
    due_date = fields.Date()
    state = fields.Selection(
        [("pending", "Pending"), ("done", "Done")], default="pending", required=True, tracking=True
    )
    task_ids = fields.One2many("fix.project.task", "milestone_id", string="Milestone Tasks")

    def action_complete(self):
        for rec in self:
            open_tasks = rec.task_ids.filtered(lambda t: t.state not in ("done", "cancelled"))
            if open_tasks:
                raise UserError("%d task(s) still open in milestone" % len(open_tasks))
            rec.state = "done"
            publish(
                self.env,
                "project.milestone_completed",
                "fix.project.milestone",
                rec.id,
                {"milestone": rec.name, "project": rec.project_id.name},
            )


class FixProjectTask(models.Model):
    _name = "fix.project.task"
    _description = "Project Task"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id asc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    project_id = fields.Many2one("fix.project", required=True, ondelete="cascade")
    milestone_id = fields.Many2one("fix.project.milestone", string="Milestone", ondelete="set null")
    assigned_to = fields.Many2one("hr.employee", string="Assigned To")
    planned_hours = fields.Float(string="Planned Hours", default=0.0)
    actual_hours = fields.Float(string="Actual Hours", default=0.0)
    state = fields.Selection(
        [
            ("todo", "To Do"),
            ("in_progress", "In Progress"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        default="todo",
        required=True,
        tracking=True,
    )

    def action_start(self):
        for rec in self:
            rec.state = "in_progress"

    def action_done(self):
        for rec in self:
            rec.state = "done"
