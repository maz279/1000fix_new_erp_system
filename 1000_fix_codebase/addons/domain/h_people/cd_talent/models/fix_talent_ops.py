# fix_talent_ops — M58: structured interviews, practical assessments,
# background/reference checks, offers and first-90-day reviews.
# Requisitions, candidates and onboarding plans live in fix_talent.py.
#
# A09 audit M58-F4/F5: a police check was cleared by the recruiter in one
# click or rewritten from failed to clear; an assessment scored 4/100 was
# typed "passed"; one HR manager created and issued a BDT 9,999,999 offer and
# raised an issued offer's salary afterwards. Now clearance is decided by a
# verifier from the M63 inbox on an evidence file, `passed` is the score
# against the requisition's approved pass mark, and an offer is issued only
# by an approver (the CFO tier when it falls outside the M57 pay band, I7),
# with its terms pinned at approval.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_talent import _require_recruiter

# An object, never a flag: a JSON-RPC caller cannot put it in the context.
_PANEL_SYNC = object()
_PANEL_SYNC_KEY = "fix_talent_panel_sync"

RECOMMENDATIONS = [
    ("strong_yes", "Strong Yes"),
    ("yes", "Yes"),
    ("no", "No"),
    ("strong_no", "Strong No"),
]


def consolidate(recommendations):
    """The panel's result (BRU-TAO-07): any Strong No vetoes; otherwise the
    majority; a tie is No (fail closed)."""
    recs = [r for r in recommendations if r]
    if not recs:
        return False
    if "strong_no" in recs:
        return "strong_no"
    positive = sum(1 for r in recs if r in ("strong_yes", "yes"))
    negative = len(recs) - positive
    if positive > negative:
        return "strong_yes" if all(r == "strong_yes" for r in recs) else "yes"
    return "no"


class FixTalentInterview(models.Model):
    """A structured interview round with a panel. Each panelist evaluates
    independently (fix.talent.evaluation); the round's score and
    recommendation exist only once EVERY panelist has submitted (BRU-TAO-07)."""

    _name = "fix.talent.interview"
    _description = "Structured Interview"
    _inherit = ["fix.guarded.mixin"]
    _order = "scheduled_on desc, id desc"

    _FROZEN = ("notes", "interviewer_id", "candidate_id", "panelist_ids")

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    candidate_id = fields.Many2one("fix.candidate", required=True, ondelete="cascade", index=True)
    requisition_id = fields.Many2one(related="candidate_id.requisition_id", store=True)
    interviewer_id = fields.Many2one(
        "hr.employee", string="Lead Interviewer", help="Always a member of the panel."
    )
    panelist_ids = fields.Many2many(
        "hr.employee",
        "fix_talent_interview_panelist_rel",
        "interview_id",
        "employee_id",
        string="Interview Panel",
    )
    evaluation_ids = fields.One2many(
        "fix.talent.evaluation", "interview_id", string="Panel Evaluations"
    )
    panel_size = fields.Integer(compute="_compute_panel", store=True, string="Panel Size")
    panel_submitted = fields.Integer(compute="_compute_panel", store=True, string="Submitted")
    panel_complete = fields.Boolean(compute="_compute_panel", store=True, string="Panel Complete")
    scheduled_on = fields.Datetime(required=True)
    round_no = fields.Integer(string="Round", default=1)
    competency_code = fields.Char(string="Focus Competency Code")
    # The panel's consolidated result: empty until every panelist submitted,
    # so nobody, the recruiter included, sees a partial result.
    score = fields.Float(string="Panel Score (1-5)", compute="_compute_panel", store=True)
    recommendation = fields.Selection(
        RECOMMENDATIONS, string="Panel Recommendation", compute="_compute_panel", store=True
    )
    notes = fields.Text(string="Coordinator Notes", help="Logistics only; never an evaluation.")
    completed_on = fields.Datetime(readonly=True, copy=False)
    state = fields.Selection(
        [("scheduled", "Scheduled"), ("done", "Completed"), ("cancelled", "Cancelled")],
        required=True,
        default="scheduled",
    )

    _score_range = models.Constraint("CHECK (score >= 0 AND score <= 5)", "Interview score is 0-5")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "completed_on"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(r.state != "scheduled" for r in self):
            locked |= set(self._FROZEN)
        return locked

    @api.depends("evaluation_ids.state", "evaluation_ids.score", "evaluation_ids.recommendation")
    def _compute_panel(self):
        # read with sudo: the compute runs as whoever triggered it, often a
        # panelist, whose record rules hide the other evaluations
        Evaluation = self.env["fix.talent.evaluation"].sudo()
        for rec in self:
            evals = Evaluation.search([("interview_id", "=", rec.id)]) if rec.id else Evaluation
            submitted = evals.filtered(lambda e: e.state == "submitted")
            rec.panel_size = len(evals)
            rec.panel_submitted = len(submitted)
            rec.panel_complete = bool(evals) and len(submitted) == len(evals)
            if rec.panel_complete:
                rec.score = round(sum(submitted.mapped("score")) / len(submitted), 2)
                rec.recommendation = consolidate(submitted.mapped("recommendation"))
            else:
                rec.score = 0.0
                rec.recommendation = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.talent.interview") or "INT/New"
                )
        # Superuser code (seeds, migrations, data loads) is trusted, as for the
        # guard: a seeded round's typed result becomes its lead interviewer's
        # submitted evaluation, so the panel result stays computed.
        seeded = [
            (vals.pop("score", 0.0), vals.pop("recommendation", False))
            if self.env.su
            else (0.0, False)
            for vals in vals_list
        ]
        recs = super().create(vals_list)
        recs._fix_sync_panel()
        Evaluation = self.env["fix.talent.evaluation"].sudo()
        for rec, (score, recommendation) in zip(recs, seeded, strict=True):
            if recommendation and rec.interviewer_id:
                Evaluation.search(
                    [("interview_id", "=", rec.id), ("panelist_id", "=", rec.interviewer_id.id)]
                )._guarded().write(
                    {
                        "score": score or 0.0,
                        "recommendation": recommendation,
                        "state": "submitted",
                        "submitted_on": fields.Datetime.now(),
                    }
                )
        return recs

    def write(self, vals):
        if not self._fix_guard_open() and set(self._FROZEN) & set(vals):
            for rec in self:
                if rec.id and rec.state != "scheduled":
                    changed = [
                        n
                        for n in set(self._FROZEN) & set(vals)
                        if rec._fix_guard_differs(n, vals[n], rec[n])
                    ]
                    if changed:
                        raise UserError(
                            "Interview %s is %s; its panel no longer changes."
                            % (rec.name, rec.state)
                        )
        result = super().write(vals)
        if {"panelist_ids", "interviewer_id"} & set(vals) and (
            self.env.context.get(_PANEL_SYNC_KEY) is not _PANEL_SYNC
        ):
            self._fix_sync_panel()
        return result

    def _fix_sync_panel(self):
        """One evaluation per panelist; the lead interviewer is on the panel.
        A panelist who already submitted is never removed."""
        Evaluation = self.env["fix.talent.evaluation"].sudo()
        for rec in self:
            if rec.interviewer_id and rec.interviewer_id not in rec.panelist_ids:
                rec.sudo().with_context(**{_PANEL_SYNC_KEY: _PANEL_SYNC}).write(
                    {"panelist_ids": [(4, rec.interviewer_id.id)]}
                )
            evals = Evaluation.search([("interview_id", "=", rec.id)])
            have = evals.mapped("panelist_id")
            gone = evals.filtered(lambda e, r=rec: e.panelist_id not in r.panelist_ids)
            if gone.filtered(lambda e: e.state == "submitted"):
                raise UserError(
                    "%s already submitted an evaluation for %s and stays on its panel."
                    % (
                        ", ".join(
                            gone.filtered(lambda e: e.state == "submitted").mapped(
                                "panelist_id.name"
                            )
                        ),
                        rec.name,
                    )
                )
            gone._guarded().unlink()
            for emp in rec.panelist_ids - have:
                Evaluation._guarded().create(
                    {"interview_id": rec.id, "panelist_id": emp.id, "company_id": rec.company_id.id}
                )

    def _fix_resolve_employee(self, panelist):
        """An employee from an id, a record, an employee code or an exact name."""
        Employee = self.env["hr.employee"].sudo()
        if isinstance(panelist, models.BaseModel):
            return panelist[:1]
        text = str(panelist or "").strip()
        if not text:
            raise UserError("Name the panelist (employee id, code or full name).")
        if text.isdigit():
            emp = Employee.browse(int(text)).exists()
        else:
            emp = Employee.search(["|", ("employee_code", "=", text), ("name", "=", text)])
        if len(emp) != 1:
            raise UserError("No single employee matches %r." % text)
        return emp

    def action_add_panelist(self, panelist=None):
        _require_recruiter(self.env, "set an interview panel")
        emp = self._fix_resolve_employee(panelist)
        for rec in self:
            if rec.state != "scheduled":
                raise UserError("%s is %s; its panel no longer changes." % (rec.name, rec.state))
            if emp.user_id and emp.user_id == rec.candidate_id.sudo().employee_id.user_id:
                raise UserError("A candidate does not sit on their own panel.")
            rec.write({"panelist_ids": [(4, emp.id)]})
        return True

    def action_remove_panelist(self, panelist=None):
        _require_recruiter(self.env, "set an interview panel")
        emp = self._fix_resolve_employee(panelist)
        for rec in self:
            if rec.state != "scheduled":
                raise UserError("%s is %s; its panel no longer changes." % (rec.name, rec.state))
            if emp == rec.interviewer_id:
                raise UserError("Name another lead interviewer first.")
            rec.write({"panelist_ids": [(3, emp.id)]})
        return True

    def action_done(self):
        _require_recruiter(self.env, "complete an interview round")
        for rec in self:
            if rec.state != "scheduled":
                raise UserError("Complete a scheduled interview.")
            if not rec.panel_size:
                raise UserError("Name the interview panel of %s." % rec.name)
            if not rec.panel_complete:
                raise UserError(
                    "%d of %d panelists have submitted their evaluation of %s; the round "
                    "completes when every panelist has (BRU-TAO-07)."
                    % (rec.panel_submitted, rec.panel_size, rec.name)
                )
            rec._guarded().write({"state": "done", "completed_on": fields.Datetime.now()})
        return True

    def action_cancel(self):
        _require_recruiter(self.env, "cancel an interview")
        for rec in self:
            if rec.state != "scheduled":
                raise UserError("Cancel a scheduled interview.")
            rec._guarded().write({"state": "cancelled"})
        return True


class FixTalentAssessment(models.Model):
    _name = "fix.talent.assessment"
    _description = "Practical Candidate Assessment"
    _inherit = ["fix.guarded.mixin"]
    _order = "assessed_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    candidate_id = fields.Many2one("fix.candidate", required=True, ondelete="cascade", index=True)
    # BRU-TAO-12: the M22 competency tested; at hire a passed assessment
    # becomes the employee's first fix.competency.assessment (the baseline).
    competency_id = fields.Many2one(
        "fix.competency", string="M22 Competency Tested", ondelete="restrict"
    )
    competency_code = fields.Char(
        string="Competency Tested (code)", help="Set from the M22 competency when one is named."
    )
    level = fields.Selection(
        [
            ("l1", "L1 - Aware"),
            ("l2", "L2 - Assisted"),
            ("l3", "L3 - Independent"),
            ("l4", "L4 - Expert / Trainer"),
        ],
        string="Observed Level",
        default="l2",
        help="Carried to the M22 baseline assessment.",
    )
    baseline_id = fields.Many2one(
        "fix.competency.assessment", string="M22 Baseline", readonly=True, copy=False
    )
    baseline_on = fields.Datetime(string="Baseline Carried On", readonly=True, copy=False)
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
    pass_mark = fields.Float(
        related="candidate_id.requisition_id.assessment_pass_mark", string="Pass Mark %"
    )
    # A09 audit M58-18: `passed` was typed, so 4/100 counted as a pass.
    passed = fields.Boolean(string="Passed", compute="_compute_passed", store=True)
    notes = fields.Char()

    _score_range = models.Constraint(
        "CHECK (score >= 0 AND score <= 100)", "Assessment score is a 0-100 percentage"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"baseline_id", "baseline_on"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(r.baseline_id for r in self):
            locked |= {"score", "competency_id", "competency_code", "level", "assessor_id"}
        return locked

    def _fix_code_vals(self, vals):
        if vals.get("competency_id"):
            vals["competency_code"] = (
                self.env["fix.competency"].sudo().browse(vals["competency_id"]).code
            )
        return vals

    def write(self, vals):
        # `passed` is computed; a direct write would stand until the next recompute.
        if "passed" in vals and not self.env.su:
            raise UserError(
                "%s is computed and cannot be set directly." % self._fields["passed"].string
            )
        frozen = {"score", "competency_id", "level", "assessor_id", "candidate_id"} & set(vals)
        if frozen and not self._fix_guard_open():
            for rec in self:
                if rec.baseline_id and any(
                    rec._fix_guard_differs(n, vals[n], rec[n]) for n in frozen
                ):
                    raise UserError(
                        "%s is the employee's M22 baseline; it no longer changes." % rec.name
                    )
        return super().write(self._fix_code_vals(dict(vals)))

    @api.depends("score", "candidate_id.requisition_id.assessment_pass_mark")
    def _compute_passed(self):
        for rec in self:
            mark = rec.candidate_id.requisition_id.assessment_pass_mark
            rec.passed = bool(mark and rec.score >= mark)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.talent.assessment") or "TASM/New"
                )
            self._fix_code_vals(vals)
        return super().create(vals_list)


class FixTalentCheck(models.Model):
    """A background check. A negative outcome is recorded; a CLEAR outcome is
    decided by a verifier (not the requester) from the M63 inbox, on file."""

    _name = "fix.talent.check"
    _description = "Reference / Background Check"
    _inherit = ["fix.people.approval.mixin"]
    _order = "id desc"

    _approval_domain = "hr_background_check"
    _approval_apply_method = "action_clear"
    _approval_group = "cd_talent.group_background_verifier"

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
    completed_on = fields.Date(readonly=True)
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
    evidence_file = fields.Binary(string="Verification Evidence", attachment=True, copy=False)
    evidence_filename = fields.Char(copy=False)
    verified_by_id = fields.Many2one("res.users", string="Verified By", readonly=True, copy=False)
    verified_on = fields.Datetime(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "result",
            "completed_on",
            "verified_by_id",
            "verified_on",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(r.result == "clear" or r.approval_state == "pending" for r in self):
            locked |= {"evidence_file", "evidence_filename", "check_type", "candidate_id"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.talent.check") or "CHK/New"
        return super().create(vals_list)

    def write(self, vals):
        frozen = {"evidence_file", "check_type", "candidate_id"} & set(vals)
        if frozen and not self._fix_guard_open():
            for rec in self:
                if rec.id and (rec.result == "clear" or rec.approval_state == "pending"):
                    raise UserError(
                        "Check %s is cleared or awaiting its verifier; its evidence is frozen."
                        % rec.name
                    )
        return super().write(vals)

    def action_request_approval(self, justification=None):
        _require_recruiter(self.env, "send a check for verification")
        for rec in self:
            if rec.result == "clear":
                raise UserError("%s is already clear." % rec.name)
            if not rec.evidence_file:
                raise UserError(
                    "Attach the verification evidence (certificate, reference letter, PCC) "
                    "to %s before sending it to the verifier." % rec.name
                )
        return super().action_request_approval(justification=justification)

    def action_clear(self):
        """Routed apply method: the verifier clears the check."""
        self._approval_assert_routed()
        self._people_assert_not_conflicted()
        for rec in self:
            if not rec.evidence_file:
                raise UserError("%s has no verification evidence on file." % rec.name)
            rec._guarded().write(
                {
                    "result": "clear",
                    "completed_on": fields.Date.context_today(rec),
                    "verified_by_id": rec._people_decider().id,
                    "verified_on": fields.Datetime.now(),
                }
            )
        return True

    def _fix_record_negative(self, result, reason):
        _require_recruiter(self.env, "record a check outcome")
        if not (reason or "").strip():
            raise UserError("Say what the check found.")
        for rec in self:
            if rec.approval_state == "pending":
                raise UserError("%s is with its verifier." % rec.name)
            rec._guarded().write(
                {
                    "result": result,
                    "completed_on": fields.Date.context_today(rec),
                    "notes": reason.strip(),
                    "verified_by_id": False,
                    "verified_on": False,
                }
            )
            if rec.approval_state == "approved":
                rec._approval_void("the check was re-recorded as %s" % result)
        return True

    def action_mark_failed(self, reason=None):
        return self._fix_record_negative("failed", reason)

    def action_mark_discrepancy(self, reason=None):
        return self._fix_record_negative("discrepancy", reason)


class FixTalentOffer(models.Model):
    """An offer is issued only once someone other than its maker approves it."""

    _name = "fix.talent.offer"
    _description = "Employment Offer"
    _inherit = ["mail.thread", "fix.people.approval.mixin"]
    _order = "issued_on desc, id desc"

    _approval_domain = "hr_offer"
    _approval_apply_method = "action_issue"
    _approval_group = "cd_talent.group_offer_approver"
    # BRU-TAO-03: an offer outside its band (or with no band to check) goes
    # to the CFO tier.
    _OUT_OF_BAND_GROUP = "cd_entity_config.group_dofa_tier_4"
    # The terms an approval covers; pinned at issue.
    _TERMS = (
        "candidate_id",
        "position_id",
        "gross_salary",
        "basic_salary",
        "joining_date",
        "contract_type",
        "currency_id",
        "valid_until",
    )

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
    basic_salary = fields.Monetary(
        currency_field="currency_id",
        string="Basic Monthly",
        help="Carried to the draft employment contract (I6); the rest of the gross is "
        "carried as other allowance.",
    )
    contract_type = fields.Selection(
        [
            ("permanent", "Permanent"),
            ("probation", "Probation"),
            ("fixed_term", "Fixed Term"),
            ("part_time", "Part Time"),
        ],
        default="probation",
        required=True,
    )
    issued_on = fields.Date(readonly=True, copy=False)
    valid_until = fields.Date()
    joining_date = fields.Date()
    band_id = fields.Many2one(
        "fix.compensation.band", compute="_compute_band", string="Pay Band (M57)"
    )
    in_band = fields.Boolean(compute="_compute_band", string="Within Band")
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True, copy=False)
    approved_on = fields.Datetime(readonly=True, copy=False)
    approved_gross = fields.Monetary(currency_field="currency_id", readonly=True, copy=False)
    approved_in_band = fields.Boolean(readonly=True, copy=False)
    acceptance_ref = fields.Char(
        string="Candidate Acceptance Reference",
        help="The candidate's own acknowledgement: e-signature envelope, signed letter number.",
    )
    acceptance_file = fields.Binary(string="Signed Acceptance", attachment=True, copy=False)
    acceptance_filename = fields.Char(copy=False)
    responded_on = fields.Datetime(readonly=True, copy=False)
    response_recorded_by_id = fields.Many2one("res.users", readonly=True, copy=False)
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

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "issued_on",
            "approved_by_id",
            "approved_on",
            "approved_gross",
            "approved_in_band",
            "responded_on",
            "response_recorded_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(r.state != "draft" for r in self):
            locked |= set(self._TERMS)
        if any(r.state != "issued" for r in self):
            locked |= {"acceptance_ref", "acceptance_file", "acceptance_filename"}
        return locked

    # ---- the band (I7, read-only) ---------------------------------------------
    def _fix_band(self):
        """The M57 band for the offered position's grade (read-only, I7)."""
        self.ensure_one()
        Band = self.env["fix.compensation.band"].sudo()
        position = self.position_id or self.requisition_id.position_id
        if not position.grade:
            return Band
        return Band.search(
            [("grade", "=", position.grade), ("company_id", "in", (self.company_id.id, False))],
            limit=1,
        )

    @api.depends("position_id", "candidate_id", "gross_salary")
    def _compute_band(self):
        for rec in self:
            band = rec._fix_band()
            rec.band_id = band.id if band else False
            rec.in_band = bool(
                band and band.sudo().range_min <= (rec.gross_salary or 0.0) <= band.sudo().range_max
            )

    # ---- approval routing ----------------------------------------------------
    def _approval_amount(self) -> float:
        return self.gross_salary or 0.0

    def _approval_group_xmlid(self):
        if not self.in_band:
            return self._OUT_OF_BAND_GROUP
        return super()._approval_group_xmlid()

    # ---- create / write ------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.talent.offer") or "OFR/New"
            if not vals.get("position_id") and vals.get("candidate_id"):
                cand = self.env["fix.candidate"].browse(vals["candidate_id"])
                vals["position_id"] = cand.requisition_id.position_id.id or False
        return super().create(vals_list)

    def write(self, vals):
        terms = set(self._TERMS) & set(vals)
        accept = {"acceptance_ref", "acceptance_file"} & set(vals)
        void = self.browse()
        if (terms or accept) and not self._fix_guard_open():
            for rec in self:
                if not rec.id:
                    continue
                changed = [n for n in terms if rec._fix_guard_differs(n, vals[n], rec[n])]
                if changed and rec.state != "draft":
                    raise UserError(
                        "Offer %s is %s: its terms were approved and cannot change. Issue a "
                        "new offer." % (rec.name, rec.state)
                    )
                if changed and rec.approval_state == "pending":
                    void |= rec
                if (
                    accept
                    and rec.state != "issued"
                    and any(rec._fix_guard_differs(n, vals[n], rec[n]) for n in accept)
                ):
                    raise UserError("Record the candidate's acceptance on an issued offer.")
        result = super().write(vals)
        if void:
            void._approval_void("the offer's terms changed while awaiting approval")
        return result

    # ---- the issue gate (BRU-TAO-03/04/05/17) ----------------------------------
    def _fix_issue_problems(self):
        self.ensure_one()
        cand = self.candidate_id.sudo()
        problems = []
        if cand.state != "offered":
            problems.append("the candidate has not reached the offer stage")
        problems += cand._fix_requisition_problems()
        req_position = cand.requisition_id.position_id
        if req_position and self.position_id and self.position_id != req_position:
            problems.append("the offered position is not the requisition's (BRU-TAO-04)")
        if (self.gross_salary or 0.0) <= 0 or (self.basic_salary or 0.0) <= 0:
            problems.append("no gross and basic salary")
        elif self.basic_salary > self.gross_salary:
            problems.append("the basic salary exceeds the gross")
        today = fields.Date.context_today(self)
        if not self.joining_date or self.joining_date < today:
            problems.append("no joining date on or after today")
        if self.valid_until and self.valid_until < today:
            problems.append("the offer's validity has passed")
        problems += cand._fix_interview_problems()
        problems += cand._fix_assessment_problems()
        problems += cand._fix_age_problems(self.joining_date)
        live = self.sudo().search(
            [
                ("candidate_id", "=", cand.id),
                ("id", "!=", self.id),
                ("state", "in", ("issued", "accepted")),
            ],
            limit=1,
        )
        if live:
            problems.append("offer %s is already live for this candidate" % live.name)
        return problems

    def _fix_raise_issue_problems(self):
        for rec in self:
            problems = rec._fix_issue_problems()
            if problems:
                raise UserError("Offer %s cannot be issued: %s." % (rec.name, "; ".join(problems)))

    def action_request_approval(self, justification=None):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft offer is sent for approval.")
        self._fix_raise_issue_problems()
        return super().action_request_approval(justification=justification)

    def action_issue(self):
        """Routed apply method: the approver issues the offer and pins its terms."""
        self._approval_assert_routed()
        self._people_assert_not_conflicted()
        for rec in self:
            if rec.state != "draft":
                raise UserError("Issue a draft offer")
        self._fix_raise_issue_problems()
        for rec in self:
            rec._guarded().write(
                {
                    "state": "issued",
                    "issued_on": fields.Date.context_today(rec),
                    "approved_by_id": rec._people_decider().id,
                    "approved_on": fields.Datetime.now(),
                    "approved_gross": rec.gross_salary,
                    "approved_in_band": rec.in_band,
                }
            )
        return True

    def action_accept(self):
        """Record the candidate's own acceptance, then hire."""
        _require_recruiter(self.env, "record an offer acceptance")
        for rec in self:
            if rec.state != "issued":
                raise UserError("Accept an issued offer")
            if not rec.acceptance_file:
                raise UserError(
                    "Attach the candidate's signed acceptance of %s first: acceptance is the "
                    "candidate's act, not a back-office click." % rec.name
                )
            if rec.valid_until and rec.valid_until < fields.Date.context_today(rec):
                raise UserError("Offer %s expired on %s." % (rec.name, rec.valid_until))
            if abs((rec.gross_salary or 0.0) - (rec.approved_gross or 0.0)) > 0.005:
                raise UserError("Offer %s no longer matches what was approved." % rec.name)
            rec._guarded().write(
                {
                    "state": "accepted",
                    "responded_on": fields.Datetime.now(),
                    "response_recorded_by_id": self.env.user.id,
                }
            )
            rec.candidate_id.action_hire(offer=rec)
        return True

    def action_decline(self):
        _require_recruiter(self.env, "record an offer decline")
        for rec in self:
            if rec.state != "issued":
                raise UserError("Decline an issued offer")
            rec._guarded().write(
                {
                    "state": "declined",
                    "responded_on": fields.Datetime.now(),
                    "response_recorded_by_id": self.env.user.id,
                }
            )
        return True

    @api.model
    def cron_expire_offers(self):
        """Issued offers past their validity expire. Idempotent; superuser."""
        due = self.sudo().search(
            [
                ("state", "=", "issued"),
                ("valid_until", "!=", False),
                ("valid_until", "<", fields.Date.context_today(self)),
            ]
        )
        due._guarded().write({"state": "expired"})
        return len(due)


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

    @api.constrains("reviewer_id", "employee_id")
    def _check_reviewer(self):
        for rec in self:
            if rec.reviewer_id and rec.reviewer_id == rec.employee_id:
                raise ValidationError("A new hire does not review their own first 90 days.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.talent.first90") or "F90/New"
                )
        return super().create(vals_list)
