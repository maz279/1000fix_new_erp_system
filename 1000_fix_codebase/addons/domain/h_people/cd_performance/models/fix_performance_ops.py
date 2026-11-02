# fix_performance_ops — M57: goals, review cycles, PIPs, recognition and
# succession plans. Scorecards, incentive runs/lines and compensation bands
# live in fix_performance.py.
from odoo import api, fields, models
from odoo.exceptions import UserError


class FixPerfGoal(models.Model):
    _name = "fix.performance.goal"
    _description = "Performance Goal"
    _order = "period desc, employee_id"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade", index=True)
    parent_goal_id = fields.Many2one(
        "fix.performance.goal", string="Cascaded From", ondelete="set null"
    )
    period = fields.Char(required=True, help="YYYY-MM")
    weight = fields.Float(string="Weight %", default=20.0)
    target_value = fields.Float(string="Target")
    actual_value = fields.Float(string="Actual")
    unit = fields.Char(string="Unit")
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("achieved", "Achieved"), ("missed", "Missed")],
        required=True,
        default="draft",
    )

    _weight_range = models.Constraint(
        "CHECK (weight >= 0 AND weight <= 100)", "Goal weight is a 0-100 percentage"
    )

    def action_activate(self):
        for rec in self:
            rec.state = "active"

    def action_close(self):
        for rec in self:
            reached = rec.actual_value >= rec.target_value
            rec.state = "achieved" if reached else "missed"


class FixPerfReview(models.Model):
    _name = "fix.performance.review"
    _description = "Performance Review Cycle"
    _order = "period desc, employee_id"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade", index=True)
    reviewer_id = fields.Many2one("hr.employee", string="Reviewer")
    period = fields.Char(required=True, help="YYYY-MM or YYYY-Qn")
    self_rating = fields.Float(string="Self Rating (1-5)")
    manager_rating = fields.Float(string="Manager Rating (1-5)")
    calibrated_rating = fields.Float(string="Calibrated Rating (1-5)")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("self_review", "Self Review"),
            ("manager_review", "Manager Review"),
            ("calibrated", "Calibrated"),
            ("closed", "Closed"),
        ],
        required=True,
        default="draft",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.performance.review") or "PRV/New"
                )
        return super().create(vals_list)

    def action_manager_review(self):
        for rec in self:
            if not rec.manager_rating:
                raise UserError("Record the manager rating first")
            rec.state = "manager_review"

    def action_calibrate(self):
        for rec in self:
            if rec.state != "manager_review":
                raise UserError("Calibrate a review in manager review")
            rec.calibrated_rating = rec.calibrated_rating or rec.manager_rating
            rec.state = "calibrated"

    def action_close(self):
        for rec in self:
            if rec.state != "calibrated":
                raise UserError("Close a calibrated review")
            rec.state = "closed"


class FixPerfPip(models.Model):
    _name = "fix.performance.pip"
    _description = "Performance Improvement Plan"
    _order = "start_date desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade", index=True)
    mentor_id = fields.Many2one("hr.employee", string="Mentor")
    start_date = fields.Date(required=True, default=fields.Date.context_today)
    end_date = fields.Date(required=True)
    reason = fields.Text()
    outcome = fields.Selection(
        [("improved", "Improved"), ("extended", "Extended"), ("exit", "Exit")],
    )
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("closed", "Closed")],
        required=True,
        default="draft",
    )

    _dates_ordered = models.Constraint(
        "CHECK (end_date >= start_date)", "PIP end cannot precede its start"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.performance.pip") or "PIP/New"
                )
        return super().create(vals_list)

    def action_start(self):
        for rec in self:
            rec.state = "active"

    def action_close(self):
        for rec in self:
            if not rec.outcome:
                raise UserError("Record the PIP outcome before closing")
            rec.state = "closed"


class FixPerfRecognition(models.Model):
    _name = "fix.performance.recognition"
    _description = "Recognition Award"
    _order = "awarded_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade", index=True)
    award_type = fields.Selection(
        [
            ("spot", "Spot Award"),
            ("monthly", "Employee of the Month"),
            ("quarterly", "Quarterly Excellence"),
            ("values", "Values Champion"),
        ],
        required=True,
        default="spot",
    )
    awarded_on = fields.Date(required=True, default=fields.Date.context_today)
    citation = fields.Char()
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    prize_amount = fields.Monetary(currency_field="currency_id", string="Prize")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.performance.recognition")
                    or "RECG/New"
                )
        return super().create(vals_list)


class FixSuccessionPlan(models.Model):
    _name = "fix.succession.plan"
    _description = "Succession Plan"
    _order = "position_name, id"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    position_name = fields.Char(string="Key Position", required=True)
    incumbent_id = fields.Many2one("hr.employee", string="Incumbent")
    successor_id = fields.Many2one("hr.employee", string="Ready Successor")
    readiness = fields.Selection(
        [("ready_now", "Ready Now"), ("1_2_years", "1-2 Years"), ("2_3_years", "2-3 Years")],
        required=True,
        default="1_2_years",
    )
    risk = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        required=True,
        default="medium",
    )
    notes = fields.Char()
