# fix_itsm_ops — M66 (IT change management + IT asset register) and M67
# (project stage-gate reviews). ITSM tickets live in fix_itsm.py; projects,
# milestones and tasks live in cd_ppm.
from odoo import api, fields, models
from odoo.exceptions import UserError


class FixItsmChange(models.Model):
    _name = "fix.itsm.change"
    _description = "IT Change Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "planned_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    title = fields.Char(required=True)
    change_type = fields.Selection(
        [("standard", "Standard"), ("normal", "Normal"), ("emergency", "Emergency")],
        required=True,
        default="normal",
    )
    risk = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        required=True,
        default="medium",
    )
    requested_by_id = fields.Many2one("hr.employee", string="Requested By")
    planned_on = fields.Date(required=True, default=fields.Date.context_today)
    rollback_plan = fields.Text()
    change_window_hours = fields.Integer(default=2)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("approved", "Approved"),
            ("implemented", "Implemented"),
            ("rolled_back", "Rolled Back"),
            ("rejected", "Rejected"),
        ],
        required=True,
        default="draft",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.itsm.change") or "CHG/New"
        return super().create(vals_list)

    def action_approve(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Approve a draft change")
            rec.state = "approved"

    def action_implement(self):
        for rec in self:
            if rec.state != "approved":
                raise UserError("Implement an approved change")
            rec.state = "implemented"

    def action_rollback(self):
        for rec in self:
            if rec.state != "implemented":
                raise UserError("Roll back an implemented change")
            rec.state = "rolled_back"


class FixItsmAsset(models.Model):
    _name = "fix.itsm.asset"
    _description = "Internal IT Asset"
    _order = "name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    asset_tag = fields.Char(required=True)
    asset_kind = fields.Selection(
        [
            ("laptop", "Laptop"),
            ("desktop", "Desktop"),
            ("phone", "Phone"),
            ("server", "Server"),
            ("network", "Network Gear"),
            ("peripheral", "Peripheral"),
        ],
        required=True,
        default="laptop",
    )
    assigned_to_id = fields.Many2one("hr.employee", string="Assigned To")
    serial_no = fields.Char()
    warranty_end = fields.Date()
    os_version = fields.Char(string="OS / Firmware")
    state = fields.Selection(
        [
            ("in_service", "In Service"),
            ("in_stock", "In Stock"),
            ("repair", "Under Repair"),
            ("retired", "Retired"),
        ],
        required=True,
        default="in_stock",
    )

    _tag_unique = models.Constraint(
        "UNIQUE (asset_tag, company_id)", "An asset tag is unique per company"
    )


class FixProjectGate(models.Model):
    _name = "fix.project.gate"
    _description = "Project Stage-Gate Review"
    _order = "review_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    project_id = fields.Many2one("fix.project", required=True, ondelete="cascade", index=True)
    gate = fields.Selection(
        [
            ("g1_initiation", "G1 Initiation"),
            ("g2_planning", "G2 Planning"),
            ("g3_execution", "G3 Execution"),
            ("g4_uat", "G4 UAT"),
            ("g5_closure", "G5 Closure"),
        ],
        required=True,
        default="g2_planning",
    )
    review_on = fields.Date(required=True, default=fields.Date.context_today)
    reviewer_id = fields.Many2one("hr.employee", string="Reviewer")
    checklist_passed = fields.Boolean(default=False)
    findings = fields.Text()
    decision = fields.Selection(
        [("pass", "Pass"), ("conditional", "Conditional Pass"), ("fail", "Fail")],
    )
    state = fields.Selection(
        [("scheduled", "Scheduled"), ("held", "Held"), ("closed", "Closed")],
        required=True,
        default="scheduled",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.project.gate") or "GATE/New"
                )
        return super().create(vals_list)

    def action_hold(self):
        for rec in self:
            if not rec.decision:
                raise UserError("Record the gate decision before holding the review")
            rec.state = "held"

    def action_close(self):
        for rec in self:
            if rec.state != "held":
                raise UserError("Close a review that has been held")
            rec.state = "closed"
