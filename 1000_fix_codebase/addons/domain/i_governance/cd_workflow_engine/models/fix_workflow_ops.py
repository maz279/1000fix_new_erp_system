# fix_workflow_ops — M63: workflow instances, unified task inbox, business
# rules and approval substitution/OOO. The automation register (fix.automation)
# and the DoA matrix (fix.approval.matrix) live in fix_workflow_engine.py.
from odoo import api, fields, models
from odoo.exceptions import UserError


class FixWorkflowInstance(models.Model):
    _name = "fix.workflow.instance"
    _description = "Workflow Instance"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "started_at desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    automation_id = fields.Many2one("fix.automation", string="Definition", index=True)
    res_model = fields.Char(string="Record Model", index=True)
    res_id = fields.Integer(string="Record ID", index=True)
    started_at = fields.Datetime(required=True, default=fields.Datetime.now)
    finished_at = fields.Datetime()
    escalated = fields.Boolean(default=False)
    state = fields.Selection(
        [
            ("running", "Running"),
            ("completed", "Completed"),
            ("failed", "Failed"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="running",
    )
    log = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.workflow.instance") or "WFI/New"
                )
        return super().create(vals_list)

    def action_complete(self):
        for rec in self:
            if rec.state != "running":
                raise UserError("Complete a running instance")
            rec.write({"state": "completed", "finished_at": fields.Datetime.now()})

    def action_fail(self):
        for rec in self:
            if rec.state != "running":
                raise UserError("Fail a running instance")
            rec.write({"state": "failed", "finished_at": fields.Datetime.now()})

    def action_escalate(self):
        for rec in self:
            rec.escalated = True


class FixWorkflowTask(models.Model):
    _name = "fix.workflow.task"
    _description = "Unified Task Inbox Entry"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "created_at desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    instance_id = fields.Many2one("fix.workflow.instance", string="Workflow Instance")
    task_type = fields.Selection(
        [
            ("approval", "Approval"),
            ("review", "Review"),
            ("data_entry", "Data Entry"),
            ("exception", "Exception Handling"),
        ],
        required=True,
        default="approval",
    )
    res_model = fields.Char(string="Record Model")
    res_id = fields.Integer(string="Record ID")
    assigned_to_id = fields.Many2one("hr.employee", string="Assigned To", index=True)
    created_at = fields.Datetime(required=True, default=fields.Datetime.now)
    due_at = fields.Datetime()
    decided_at = fields.Datetime()
    decision = fields.Selection(
        [("approved", "Approved"), ("rejected", "Rejected"), ("returned", "Returned for Info")],
    )
    state = fields.Selection(
        [("pending", "Pending"), ("done", "Done"), ("cancelled", "Cancelled")],
        required=True,
        default="pending",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.workflow.task") or "TSK/New"
                )
        return super().create(vals_list)

    def action_approve(self):
        for rec in self:
            if rec.state != "pending":
                raise UserError("Decide a pending task")
            rec.write(
                {"state": "done", "decision": "approved", "decided_at": fields.Datetime.now()}
            )

    def action_reject(self):
        for rec in self:
            if rec.state != "pending":
                raise UserError("Decide a pending task")
            rec.write(
                {"state": "done", "decision": "rejected", "decided_at": fields.Datetime.now()}
            )


class FixBusinessRule(models.Model):
    _name = "fix.business.rule"
    _description = "Business Rule"
    _order = "code"

    code = fields.Char(required=True)
    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    domain_area = fields.Char(string="Process Area")
    rule_type = fields.Selection(
        [
            ("validation", "Validation"),
            ("derivation", "Derivation"),
            ("gate", "Gate / Hard Block"),
            ("escalation", "Escalation Trigger"),
        ],
        required=True,
        default="validation",
    )
    expression = fields.Text(string="Rule Expression", required=True)
    error_message = fields.Char(string="Refusal Message")
    automation_id = fields.Many2one("fix.automation", string="Linked Automation")
    active = fields.Boolean(default=True)
    version = fields.Integer(default=1)
    last_changed_by = fields.Many2one("res.users", default=lambda self: self.env.user)
    last_changed_on = fields.Datetime(default=fields.Datetime.now)

    _code_unique = models.Constraint(
        "UNIQUE (code, company_id)", "A business rule code is unique per company"
    )

    def action_new_version(self):
        for rec in self:
            rec.version += 1
            rec.last_changed_by = self.env.user.id
            rec.last_changed_on = fields.Datetime.now()


class FixApprovalSubstitution(models.Model):
    _name = "fix.approval.substitution"
    _description = "Approval Substitution / OOO"
    _order = "start_date desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    absent_approver_id = fields.Many2one(
        "hr.employee", string="Absent Approver", required=True, index=True
    )
    delegate_id = fields.Many2one("hr.employee", string="Delegate", required=True)
    start_date = fields.Date(required=True, default=fields.Date.context_today)
    end_date = fields.Date(required=True)
    reason = fields.Char()
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("expired", "Expired")],
        required=True,
        default="draft",
    )

    _dates_ordered = models.Constraint(
        "CHECK (end_date >= start_date)", "Substitution end cannot precede its start"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.approval.substitution") or "SUB/New"
                )
        return super().create(vals_list)

    def action_activate(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Activate a draft substitution")
            rec.state = "active"

    def action_expire(self):
        for rec in self:
            rec.state = "expired"
