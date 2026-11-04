# fix_competency_ops — M22: assessments, learning paths, OJT mentoring records
# and ISO/brand audit evidence. Competencies, certifications and training
# courses/enrolments live in fix_competency.py.
#
# A09 workflow audit (M22-F6/F7): an assessee was his own assessor (L4, 100,
# passed); 'passed' was a free tick (5 % passed); a trainee mentored himself
# to 'competent'; one user created, submitted and accepted ISO 9001 evidence
# with no file; the P03 form moved evidence straight to 'accepted'; and every
# employee read every colleague's assessment result (S2, BRU-LMS-12).
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from .fix_competency import TRAINING, VERIFIER, changed_fields, guard_first, require_group


class FixCompetencyAssessment(models.Model):
    _name = "fix.competency.assessment"
    _description = "Competency Assessment"
    # The guard mixin only for its comparison helper: nothing is guarded; a
    # result is immutable for everyone but trusted code (write below).
    _inherit = ["fix.guarded.mixin"]
    _order = "assessed_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade", index=True)
    competency_id = fields.Many2one("fix.competency", required=True, ondelete="restrict")
    assessed_on = fields.Date(required=True, default=fields.Date.context_today)
    assessor_id = fields.Many2one("hr.employee", string="Assessor")
    level = fields.Selection(
        [
            ("l1", "L1 - Aware"),
            ("l2", "L2 - Assisted"),
            ("l3", "L3 - Independent"),
            ("l4", "L4 - Expert / Trainer"),
        ],
        required=True,
        default="l2",
    )
    score = fields.Float(string="Score %")
    # FR-LMS-026: the result follows the score and the competency's pass mark;
    # it is not a tick-box.
    passed = fields.Boolean(string="Passed", compute="_compute_passed", store=True)
    notes = fields.Char()

    _score_range = models.Constraint(
        "CHECK (score >= 0 AND score <= 100)", "Assessment score is a 0-100 percentage"
    )

    _RESULT = frozenset(
        {"employee_id", "competency_id", "assessed_on", "assessor_id", "level", "score"}
    )

    @api.depends("score", "competency_id.pass_mark")
    def _compute_passed(self):
        for rec in self:
            mark = rec.competency_id.pass_mark or 0.0
            rec.passed = bool(mark > 0 and (rec.score or 0.0) >= mark)

    @api.constrains("employee_id", "assessor_id")
    def _check_assessor(self):
        for rec in self:
            if not rec.assessor_id and not self.env.su:
                raise ValidationError("An assessment names its assessor (BRU-LMS-06).")
            if rec.assessor_id == rec.employee_id:
                raise ValidationError("BRU-LMS-06: nobody assesses themself.")

    @api.model_create_multi
    def create(self, vals_list):
        Employee = self.env["hr.employee"].sudo()
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.competency.assessment") or "ASMT/New"
                )
            if not self.env.su and "passed" in vals:
                raise UserError(
                    "The result follows the score and the competency's pass mark; it is not ticked."
                )
            if (
                not self.env.su
                and vals.get("employee_id")
                and Employee.browse(vals["employee_id"]).user_id == self.env.user
            ):
                raise UserError("You cannot record your own assessment.")
        records = super().create(vals_list)
        if not self.env.su:
            records._fix_check_attempts()
        return records

    def _fix_check_attempts(self):
        """BRU-LMS-09: attempts are limited by the competency's policy."""
        for rec in self:
            limit = rec.competency_id.attempt_limit
            if not limit:
                continue
            prior = self.sudo().search(
                [
                    ("id", "!=", rec.id),
                    ("employee_id", "=", rec.employee_id.id),
                    ("competency_id", "=", rec.competency_id.id),
                ]
            )
            if any(prior.mapped("passed")):
                continue
            if len(prior) >= limit:
                raise UserError(
                    "%s has used the %d attempts allowed for %s: escalate to the manager "
                    "and HR (BRU-LMS-09, AUT-LMS-11)."
                    % (rec.employee_id.name, limit, rec.competency_id.name)
                )

    def write(self, vals):
        if not self.env.su:
            changed = changed_fields(self, vals, self._RESULT | {"passed"})
            if changed:
                raise UserError(
                    "An assessment result is not edited (%s); record a new assessment."
                    % ", ".join(sorted(changed))
                )
        return super().write(vals)


class FixLearningPath(models.Model):
    _name = "fix.learning.path"
    _description = "Learning Path"
    _order = "name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    target_role = fields.Char(string="Target Role")
    competency_ids = fields.Many2many("fix.competency", string="Target Competencies")
    course_ids = fields.Many2many("fix.training.course", string="Courses in Path")
    min_level = fields.Selection(
        [
            ("l1", "L1 - Aware"),
            ("l2", "L2 - Assisted"),
            ("l3", "L3 - Independent"),
            ("l4", "L4 - Expert / Trainer"),
        ],
        required=True,
        default="l3",
    )
    active = fields.Boolean(default=True)


class FixOjtRecord(models.Model):
    _name = "fix.ojt.record"
    _description = "OJT / Mentoring Record"
    _inherit = ["fix.guarded.mixin"]
    _order = "date_from desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade", index=True)
    mentor_id = fields.Many2one("hr.employee", string="Mentor")
    competency_id = fields.Many2one("fix.competency", string="Focus Competency")
    date_from = fields.Date(required=True, default=fields.Date.context_today)
    date_to = fields.Date()
    hours = fields.Float(string="Hours")
    outcome = fields.Selection(
        [
            ("ongoing", "Ongoing"),
            ("competent", "Declared Competent"),
            ("extended", "Extended"),
            ("discontinued", "Discontinued"),
        ],
        required=True,
        default="ongoing",
    )
    notes = fields.Char()
    signed_off_by_id = fields.Many2one("res.users", string="Signed Off By", readonly=True)
    signed_off_at = fields.Datetime(string="Signed Off At", readonly=True)

    _FROZEN_WHEN_SIGNED = frozenset(
        {"employee_id", "mentor_id", "competency_id", "date_from", "date_to", "hours", "company_id"}
    )

    def _fix_guarded_fields(self) -> set:
        # FR-LMS-027: the outcome is the mentor's sign-off, not a field to type.
        return super()._fix_guarded_fields() | {"outcome", "signed_off_by_id", "signed_off_at"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(rec.signed_off_by_id for rec in self):
            locked = locked | self._FROZEN_WHEN_SIGNED
        return locked

    @api.constrains("employee_id", "mentor_id")
    def _check_mentor(self):
        for rec in self:
            if rec.mentor_id and rec.mentor_id == rec.employee_id:
                raise ValidationError("A trainee cannot be their own mentor.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.ojt.record") or "OJT/New"
        return super().create(vals_list)

    def write(self, vals):
        guard_first(self, vals)
        if not self._fix_guard_open():
            frozen = changed_fields(
                self.filtered(lambda r: r.signed_off_by_id), vals, self._FROZEN_WHEN_SIGNED
            )
            if frozen:
                raise UserError(
                    "A signed-off OJT record is final (%s)." % ", ".join(sorted(frozen))
                )
        return super().write(vals)

    def action_sign_off(self, outcome="competent"):
        """The supervising technician (the mentor) signs the outcome off."""
        outcome = (outcome or "").strip().lower()
        valid = {"competent", "extended", "discontinued"}
        if outcome not in valid:
            raise UserError("The outcome is one of: %s." % ", ".join(sorted(valid)))
        user = self.env.user
        for rec in self:
            if rec.signed_off_by_id:
                raise UserError("%s is already signed off." % rec.name)
            if not rec.mentor_id:
                raise UserError("Name the mentor before signing off.")
            mentor_user = rec.mentor_id.sudo().user_id
            trainee_user = rec.employee_id.sudo().user_id
            if not self.env.su:
                if trainee_user == user:
                    raise UserError("A trainee does not sign off their own OJT.")
                if mentor_user and mentor_user != user:
                    raise AccessError(
                        "Only the mentor, %s, signs this OJT off." % rec.mentor_id.name
                    )
                if not mentor_user and not user.has_group(TRAINING):
                    raise AccessError(
                        "A Training Manager signs off for a mentor with no user account."
                    )
            if outcome == "competent" and not (rec.hours or 0) > 0:
                raise UserError("Record the supervised hours before declaring competence.")
            rec.sudo()._guarded().write(
                {
                    "outcome": outcome,
                    "signed_off_by_id": user.id,
                    "signed_off_at": fields.Datetime.now(),
                }
            )
        return True


class FixAuditEvidence(models.Model):
    _name = "fix.audit.evidence"
    _description = "ISO / Brand Audit Evidence"
    _inherit = ["fix.guarded.mixin"]
    _order = "collected_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    evidence_type = fields.Selection(
        [
            ("iso_9001", "ISO 9001:2015"),
            ("brand_audit", "Brand Audit"),
            ("internal_audit", "Internal Audit"),
            ("skills_audit", "Skills Audit"),
        ],
        required=True,
        default="brand_audit",
    )
    standard_ref = fields.Char(string="Standard Clause / Brand Requirement")
    collected_on = fields.Date(required=True, default=fields.Date.context_today)
    reference = fields.Char(string="Evidence Reference")
    attachment_note = fields.Char(string="Attachment / Location")
    employee_id = fields.Many2one("hr.employee", string="Audited Technician / Staff")
    brand_id = fields.Many2one("fix.brand", string="Audited OEM Brand")
    dossier_summary = fields.Text(string="Compiled ISO 9001 Cl. 7.2 Dossier")
    evidence_file = fields.Binary(string="Audit Evidence Scan", attachment=True)
    evidence_filename = fields.Char(string="Evidence Filename")
    notes = fields.Text(string="Auditor Notes")
    valid_until = fields.Date()
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"), ("accepted", "Accepted")],
        required=True,
        default="draft",
    )
    submitted_by_id = fields.Many2one("res.users", string="Submitted By", readonly=True)
    submitted_at = fields.Datetime(string="Submitted At", readonly=True)
    accepted_by_id = fields.Many2one("res.users", string="Accepted By", readonly=True)
    accepted_at = fields.Datetime(string="Accepted At", readonly=True)

    _ARTEFACT = frozenset(
        {
            "name",
            "evidence_type",
            "standard_ref",
            "collected_on",
            "reference",
            "attachment_note",
            "employee_id",
            "brand_id",
            "dossier_summary",
            "evidence_file",
            "evidence_filename",
            "valid_until",
            "company_id",
        }
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "submitted_by_id",
            "submitted_at",
            "accepted_by_id",
            "accepted_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(rec.state != "draft" for rec in self):
            locked = locked | self._ARTEFACT
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.audit.evidence") or "AUD/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        guard_first(self, vals)
        if not self._fix_guard_open():
            frozen = changed_fields(
                self.filtered(lambda r: r.state != "draft"), vals, self._ARTEFACT
            )
            if frozen:
                raise UserError(
                    "Submitted or accepted audit evidence is not edited (%s)."
                    % ", ".join(sorted(frozen))
                )
        return super().write(vals)

    def action_submit(self):
        require_group(self.env, TRAINING, "Submitting audit evidence")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only draft evidence is submitted.")
            if not rec.evidence_file:
                raise UserError("Attach the evidence file before submitting (ISO 9001 cl. 7.2).")
            rec._guarded().write(
                {
                    "state": "submitted",
                    "submitted_by_id": self.env.user.id,
                    "submitted_at": fields.Datetime.now(),
                }
            )
        return True

    def action_accept(self):
        """A verifier other than the person who compiled or submitted it accepts."""
        require_group(self.env, VERIFIER, "Accepting audit evidence")
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Accept a submitted evidence record")
            if not self.env.su and self.env.user in (rec.submitted_by_id | rec.create_uid):
                raise UserError(
                    "Evidence is accepted by someone other than who compiled or submitted it."
                )
            if not rec.evidence_file:
                raise UserError("Evidence with no file is not accepted.")
            rec._guarded().write(
                {
                    "state": "accepted",
                    "accepted_by_id": self.env.user.id,
                    "accepted_at": fields.Datetime.now(),
                }
            )
        return True

    def action_reject(self, reason=None):
        require_group(self.env, VERIFIER, "Returning audit evidence")
        reason = (reason or "").strip()
        if not reason:
            raise UserError("Say why the evidence is returned.")
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Only submitted evidence is returned.")
            rec._guarded().write(
                {
                    "state": "draft",
                    "submitted_by_id": False,
                    "submitted_at": False,
                    "notes": "%s\nReturned by %s: %s"
                    % (rec.notes or "", self.env.user.name, reason),
                }
            )
        return True

    def action_compile_iso_dossier(self):
        """ISO 9001:2015 Clause 7.2 Competence Dossier Compiler (RAP-M22-06)."""
        self.ensure_one()
        if self.state != "draft":
            raise UserError("Compile the dossier before the evidence is submitted.")
        today = fields.Date.context_today(self)
        emp_domain = [("employee_id", "=", self.employee_id.id)] if self.employee_id else []
        certs = self.env["fix.certification"].search(emp_domain)
        current = certs.filtered(
            lambda c: c.state == "valid" and (not c.expires_on or c.expires_on >= today)
        )
        trainings = self.env["fix.training.enrollment"].search(
            [*emp_domain, ("state", "=", "passed")]
        )
        assessments = self.env["fix.competency.assessment"].search(emp_domain)
        ojts = self.env["fix.ojt.record"].search(emp_domain)

        lines = [
            f"ISO 9001:2015 CLAUSE 7.2 COMPETENCE DOSSIER — {self.name}",
            f"Standard / Clause: {self.standard_ref or 'ISO 9001:2015 Cl. 7.2'}",
            f"Technician: {self.employee_id.name if self.employee_id else 'All Certified Staff'}",
            f"Valid Certifications: {len(current)} (of {len(certs)} on record)",
            f"Passed Training Courses: {len(trainings)}",
            f"Competency Assessments: {len(assessments)} "
            f"({len(assessments.filtered('passed'))} passed)",
            f"OJT Mentoring Hours: {sum(ojts.mapped('hours')):.1f}h "
            f"({len(ojts.filtered('signed_off_by_id'))} signed off)",
        ]
        summary = "\n".join(lines)
        self.write({"dossier_summary": summary})
        return {
            "evidence_id": self.id,
            "certifications": len(current),
            "passed_trainings": len(trainings),
            "assessments": len(assessments),
            "ojt_hours": sum(ojts.mapped("hours")),
            "summary": summary,
        }
