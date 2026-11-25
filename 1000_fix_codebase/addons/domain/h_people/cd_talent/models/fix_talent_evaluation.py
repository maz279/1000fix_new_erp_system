# fix_talent_evaluation — M58: one panelist's independent interview evaluation
# (BRU-TAO-07, T-06, AC-10).
#
# A09 audit M58-38: every employee read every interview score and note, and
# the "evaluation" was one record the recruiter typed. Now each panelist has
# their own evaluation:
#   * a panelist reads and writes only their own, and only until they submit
#     it (global record rules, security/fix_a09_talent_rules.xml);
#   * nobody else, the recruiter and the hiring manager included, reads any
#     evaluation of a round until EVERY panelist has submitted;
#   * a submitted evaluation never changes;
#   * rows are created and removed only by the interview's panel (sudo).
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

from .fix_talent_ops import RECOMMENDATIONS

CONTENT = ("score", "recommendation", "notes")


class FixTalentEvaluation(models.Model):
    _name = "fix.talent.evaluation"
    _description = "Interview Panel Evaluation"
    _inherit = ["fix.guarded.mixin"]
    _order = "interview_id desc, id"

    interview_id = fields.Many2one(
        "fix.talent.interview", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    requisition_id = fields.Many2one(
        related="interview_id.requisition_id", store=True, string="Requisition"
    )
    # related fields read with sudo: the panelist needs no right on the
    # candidate or the interview to know whom they are evaluating
    candidate_name = fields.Char(related="interview_id.candidate_id.name", string="Candidate")
    scheduled_on = fields.Datetime(related="interview_id.scheduled_on", string="Scheduled")
    round_no = fields.Integer(related="interview_id.round_no", string="Round")
    panelist_id = fields.Many2one("hr.employee", string="Panelist", required=True, index=True)
    panelist_user_id = fields.Many2one(
        related="panelist_id.user_id", store=True, index=True, string="Panelist User"
    )
    score = fields.Float(string="Score (1-5)")
    recommendation = fields.Selection(RECOMMENDATIONS)
    notes = fields.Text(string="Evaluation Notes")
    submitted_on = fields.Datetime(readonly=True, copy=False)
    state = fields.Selection(
        [("draft", "Not Submitted"), ("submitted", "Submitted")],
        required=True,
        default="draft",
    )

    _score_range = models.Constraint(
        "CHECK (score >= 0 AND score <= 5)", "An evaluation score is 0-5"
    )
    _one_per_panelist = models.Constraint(
        "UNIQUE (interview_id, panelist_id)", "A panelist evaluates a round once"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "submitted_on",
            "interview_id",
            "panelist_id",
            "company_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(r.state != "draft" for r in self):
            locked |= set(CONTENT)
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            raise AccessError("An evaluation is opened by naming the panelist on the interview.")
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open() and set(CONTENT) & set(vals):
            for rec in self:
                if rec.panelist_user_id != self.env.user:
                    raise AccessError("Only the panelist writes their own evaluation.")
                if rec.state != "draft":
                    raise UserError("Your evaluation of %s is submitted." % rec.candidate_name)
        return super().write(vals)

    def unlink(self):
        if not self._fix_guard_open():
            raise AccessError("An evaluation leaves only when its panelist leaves the panel.")
        return super().unlink()

    def action_submit(self):
        """The panelist submits their own evaluation; it is then final."""
        for rec in self:
            if not self.env.su and rec.panelist_user_id != self.env.user:
                raise AccessError("Only %s submits this evaluation." % rec.panelist_id.sudo().name)
            if rec.state != "draft":
                raise UserError("This evaluation is already submitted.")
            if rec.interview_id.sudo().state != "scheduled":
                raise UserError("The interview round is closed.")
            if not rec.recommendation or not rec.score:
                raise UserError("Give your score (1-5) and your recommendation before submitting.")
            rec._guarded().write({"state": "submitted", "submitted_on": fields.Datetime.now()})
        return True
