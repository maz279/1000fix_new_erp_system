# fix_talent_ops — M58: structured interviews, practical assessments,
# background/reference checks, offers and first-90-day reviews.
# Requisitions, candidates and onboarding plans live in fix_talent.py.
from odoo import api, fields, models
from odoo.exceptions import UserError


class FixTalentInterview(models.Model):
    _name = "fix.talent.interview"
    _description = "Structured Interview"
    _order = "scheduled_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    candidate_id = fields.Many2one("fix.candidate", required=True, ondelete="cascade", index=True)
    requisition_id = fields.Many2one(related="candidate_id.requisition_id", store=True)
    interviewer_id = fields.Many2one("hr.employee", string="Interviewer")
    scheduled_on = fields.Datetime(required=True)
    round_no = fields.Integer(string="Round", default=1)
    # cd_talent has no dependency on cd_competency (the M38 lesson): the
    # competency is referenced by code, not by a cross-module FK.
    competency_code = fields.Char(string="Focus Competency Code")
    score = fields.Float(string="Score (1-5)")
    recommendation = fields.Selection(
        [("strong_yes", "Strong Yes"), ("yes", "Yes"), ("no", "No"), ("strong_no", "Strong No")],
    )
    notes = fields.Text()
    state = fields.Selection(
        [("scheduled", "Scheduled"), ("done", "Completed"), ("cancelled", "Cancelled")],
        required=True,
        default="scheduled",
    )

    _score_range = models.Constraint("CHECK (score >= 0 AND score <= 5)", "Interview score is 0-5")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.talent.interview") or "INT/New"
                )
        return super().create(vals_list)

    def action_done(self):
        for rec in self:
            if not rec.recommendation:
                raise UserError("Record the recommendation before completing the interview")
            rec.state = "done"


class FixTalentAssessment(models.Model):
    _name = "fix.talent.assessment"
    _description = "Practical Candidate Assessment"
    _order = "assessed_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    candidate_id = fields.Many2one("fix.candidate", required=True, ondelete="cascade", index=True)
    competency_code = fields.Char(string="Competency Tested (code)")
    requisition_id = fields.Many2one(
        "fix.job.requisition",
        string="Requisition",
        related="candidate_id.requisition_id",
        store=True,
        readonly=True,
    )
    assessor_id = fields.Many2one("hr.employee", string="Assessor")
    assessed_on = fields.Date(required=True, default=fields.Date.context_today)
    score = fields.Float(string="Score %")
    passed = fields.Boolean(string="Passed")
    notes = fields.Char()

    _score_range = models.Constraint(
        "CHECK (score >= 0 AND score <= 100)", "Assessment score is a 0-100 percentage"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.talent.assessment") or "TASM/New"
                )
        return super().create(vals_list)


class FixTalentCheck(models.Model):
    _name = "fix.talent.check"
    _description = "Reference / Background Check"
    _order = "id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    candidate_id = fields.Many2one("fix.candidate", required=True, ondelete="cascade", index=True)
    check_type = fields.Selection(
        [
            ("reference", "Reference"),
            ("nid", "NID Verification"),
            ("education", "Education Verification"),
            ("employment", "Employment History"),
            ("police", "Police Clearance"),
        ],
        required=True,
        default="reference",
    )
    requested_on = fields.Date(required=True, default=fields.Date.context_today)
    completed_on = fields.Date()
    result = fields.Selection(
        [
            ("pending", "Pending"),
            ("clear", "Clear"),
            ("discrepancy", "Discrepancy"),
            ("failed", "Failed"),
        ],
        required=True,
        default="pending",
    )
    reference_contact = fields.Char(string="Reference Contact")
    notes = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.talent.check") or "CHK/New"
        return super().create(vals_list)

    def action_clear(self):
        for rec in self:
            rec.result = "clear"
            rec.completed_on = fields.Date.context_today(self)


class FixTalentOffer(models.Model):
    _name = "fix.talent.offer"
    _description = "Employment Offer"
    _order = "issued_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    candidate_id = fields.Many2one("fix.candidate", required=True, ondelete="cascade", index=True)
    requisition_id = fields.Many2one(related="candidate_id.requisition_id", store=True)
    position_id = fields.Many2one("fix.org.position", string="Position")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    gross_salary = fields.Monetary(currency_field="currency_id", string="Gross Monthly")
    issued_on = fields.Date(required=True, default=fields.Date.context_today)
    valid_until = fields.Date()
    joining_date = fields.Date()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("issued", "Issued"),
            ("accepted", "Accepted"),
            ("declined", "Declined"),
            ("expired", "Expired"),
        ],
        required=True,
        default="draft",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.talent.offer") or "OFR/New"
        return super().create(vals_list)

    def action_issue(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Issue a draft offer")
            rec.state = "issued"

    def action_accept(self):
        for rec in self:
            if rec.state != "issued":
                raise UserError("Accept an issued offer")
            rec.state = "accepted"
            rec.candidate_id.action_hire()

    def action_decline(self):
        for rec in self:
            if rec.state != "issued":
                raise UserError("Decline an issued offer")
            rec.state = "declined"


class FixTalentFirst90(models.Model):
    _name = "fix.talent.first90"
    _description = "First-90-Days Review"
    _order = "check_date desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade", index=True)
    plan_id = fields.Many2one("fix.onboarding.plan", string="Onboarding Plan")
    reviewer_id = fields.Many2one("hr.employee", string="Reviewing Manager")
    check_date = fields.Date(required=True, default=fields.Date.context_today)
    milestone = fields.Selection(
        [("day_30", "Day 30"), ("day_60", "Day 60"), ("day_90", "Day 90")],
        required=True,
        default="day_30",
    )
    rating = fields.Float(string="Rating (1-5)")
    on_track = fields.Boolean(string="On Track", default=True)
    notes = fields.Char()

    _rating_range = models.Constraint(
        "CHECK (rating >= 0 AND rating <= 5)", "First-90 rating is 0-5"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.talent.first90") or "F90/New"
                )
        return super().create(vals_list)
