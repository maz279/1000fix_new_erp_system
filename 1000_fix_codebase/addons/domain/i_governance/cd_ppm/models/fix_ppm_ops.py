# M67 project operations depth — templates, milestone billing and the risk/issue
# register. Projects, milestones, tasks and stage gates live in fix_ppm.py.
from odoo import api, fields, models
from odoo.exceptions import UserError


class FixProjectTemplate(models.Model):
    _name = "fix.project.template"
    _description = "Project Template"
    _order = "project_type, name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    project_type = fields.Selection(
        [
            ("internal", "Internal"),
            ("client", "Client Project"),
            ("infrastructure", "Infrastructure"),
        ],
        required=True,
        default="internal",
    )
    default_duration_days = fields.Integer(default=90)
    default_budget = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    gate_plan = fields.Char(
        help="Comma-separated gates the project must pass, e.g. g1_initiation,g2_planning"
    )
    milestone_plan = fields.Text(help="One milestone per line, in sequence.")
    wbs_plan = fields.Text(help="One task per line; prefix with the milestone name.")
    active = fields.Boolean(default=True)

    def action_instantiate(self):
        """Creates a real project (+ its milestones) from the template."""
        self.ensure_one()
        Project = self.env["fix.project"]
        Milestone = self.env["fix.project.milestone"]
        project = Project.create(
            {
                "name": "%s — from template" % self.name,
                "project_type": self.project_type,
                "budget": self.default_budget,
                "date_start": fields.Date.context_today(self),
                "state": "draft",
            }
        )
        for line in (self.milestone_plan or "").splitlines():
            name = line.strip()
            if name:
                Milestone.create({"project_id": project.id, "name": name})
        return project


class FixProjectBilling(models.Model):
    _name = "fix.project.billing"
    _description = "Milestone Billing"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "due_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    project_id = fields.Many2one(
        "fix.project", string="Project", required=True, ondelete="cascade", index=True
    )
    milestone_id = fields.Many2one("fix.project.milestone", string="Milestone")
    customer_id = fields.Many2one("res.partner", string="Customer")
    billing_type = fields.Selection(
        [
            ("milestone", "Milestone"),
            ("time_material", "Time & Material"),
            ("retainer", "Retainer"),
        ],
        required=True,
        default="milestone",
    )
    amount = fields.Monetary(required=True, currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    due_on = fields.Date(required=True, default=fields.Date.context_today)
    invoiced_on = fields.Date()
    invoice_ref = fields.Char()
    retention_pct = fields.Float(default=0.0)
    state = fields.Selection(
        [
            ("planned", "Planned"),
            ("ready", "Ready to Invoice"),
            ("invoiced", "Invoiced"),
            ("paid", "Paid"),
        ],
        required=True,
        default="planned",
        tracking=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.project.billing") or "BILL/New"
                )
        return super().create(vals_list)

    def action_mark_ready(self):
        for rec in self:
            if rec.state != "planned":
                raise UserError("Only a planned billing line can be marked ready")
            rec.state = "ready"

    def action_mark_invoiced(self):
        for rec in self:
            if rec.state != "ready":
                raise UserError("Only a ready billing line can be invoiced")
            if not rec.invoice_ref:
                raise UserError("Record the invoice reference before marking it invoiced")
            rec.write({"state": "invoiced", "invoiced_on": fields.Date.context_today(rec)})


class FixProjectRisk(models.Model):
    _name = "fix.project.risk"
    _description = "Project Risk / Issue"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "opened_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    project_id = fields.Many2one(
        "fix.project", string="Project", required=True, ondelete="cascade", index=True
    )
    kind = fields.Selection([("risk", "Risk"), ("issue", "Issue")], required=True, default="risk")
    title = fields.Char(required=True)
    description = fields.Text()
    probability = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        required=True,
        default="medium",
    )
    impact = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        required=True,
        default="medium",
    )
    severity_score = fields.Integer(
        compute="_compute_severity",
        store=True,
        help="probability x impact (1-3 each) -> 1..9; the register sorts by this.",
    )
    owner_id = fields.Many2one("res.users", string="Owner")
    mitigation = fields.Text()
    opened_on = fields.Date(required=True, default=fields.Date.context_today)
    closed_on = fields.Date()
    state = fields.Selection(
        [("open", "Open"), ("mitigating", "Mitigating"), ("closed", "Closed")],
        required=True,
        default="open",
        tracking=True,
    )

    @api.depends("probability", "impact")
    def _compute_severity(self):
        scale = {"low": 1, "medium": 2, "high": 3}
        for rec in self:
            rec.severity_score = scale.get(rec.probability, 1) * scale.get(rec.impact, 1)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.project.risk") or "RISK/New"
                )
        return super().create(vals_list)

    def action_mitigate(self):
        for rec in self:
            if rec.state != "open":
                raise UserError("Only an open risk can move to mitigating")
            rec.state = "mitigating"

    def action_close(self):
        for rec in self:
            if rec.state not in ("open", "mitigating"):
                raise UserError("This risk is already closed")
            rec.write({"state": "closed", "closed_on": fields.Date.context_today(rec)})
