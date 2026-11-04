# fix_talent — M58: requisitions, candidates and onboarding plans.
#
# A09 workflow audit (2026-11-03), M58 findings F1-F13: a hire needed nothing
# (walk-ins, draft and closed requisitions, rejected candidates, two people
# on one opening), every workflow state was writable, the requisition
# "approval" was the recruiter's own button and onboarding completed on four
# self-ticked booleans. Here:
#   * every state moves only through its transition (fix.guarded.mixin);
#   * the requisition is approved from someone else's inbox (M63, B3);
#   * the hire gate lives in the transition and checks the requisition, the
#     headcount, the accepted offer, the interview, the verified checks, the
#     assessment, consent, age and duplicates (B2);
#   * the hire creates the employee and a DRAFT contract from the offer (I6)
#     and holds the identity event until onboarding completes (M58-F6);
#   * onboarding completion reads evidence, not ticks (M58-F8).
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from .hr_employee_talent import hold_joiner

POSITIVE = ("strong_yes", "yes")
# Every hire is verified for identity and references; a field role adds the
# police clearance (BRU-TAO-06, RAP-M58-05).
REQUIRED_CHECKS = ("nid", "reference")
FIELD_ROLE_CHECKS = ("police",)


def _param(env, key, default):
    return env["ir.config_parameter"].sudo().get_param(key, default)


def _int_param(env, key, default):
    try:
        return int(_param(env, key, default) or 0)
    except (TypeError, ValueError):
        return int(default)


def _digits(value):
    return "".join(ch for ch in (value or "") if ch.isdigit())


def _require_recruiter(env, what):
    if not (env.su or env.user.has_group("cd_talent.group_talent")):
        raise AccessError("Only Recruitment may %s." % what)


class FixJobRequisition(models.Model):
    """A headcount request, approved by someone other than its requester."""

    _name = "fix.job.requisition"
    _description = "Job Requisition"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.people.approval.mixin"]

    _approval_domain = "hr_requisition"
    _approval_apply_method = "action_approve"
    _approval_group = "cd_talent.group_requisition_approver"

    # What the approval covered: frozen once the requisition is submitted.
    _FROZEN = (
        "position_id",
        "department_id",
        "openings",
        "is_field_role",
        "assessment_pass_mark",
        "company_id",
    )

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    department_id = fields.Many2one("hr.department", string="Department")
    position_id = fields.Many2one("fix.org.position", string="Position")
    openings = fields.Integer(default=1, required=True)
    is_field_role = fields.Boolean(
        string="Field / In-Home Service Role (Requires PCC & Assessment)",
        default=False,
    )
    assessment_pass_mark = fields.Float(
        string="Practical Assessment Pass Mark (%)",
        help="The score (0-100) a practical assessment must reach to pass. Set by the "
        "requester and covered by the requisition's approval; a field role cannot be "
        "submitted without one.",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("open", "Open"), ("hired", "Filled"), ("closed", "Closed")],
        default="draft",
        required=True,
        tracking=True,
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True, copy=False)
    approved_on = fields.Datetime(readonly=True, copy=False)
    approved_openings = fields.Integer(string="Approved Headcount", readonly=True, copy=False)
    hired_count = fields.Integer(compute="_compute_fill", string="Hired")
    openings_left = fields.Integer(compute="_compute_fill", string="Openings Left")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "approved_by_id",
            "approved_on",
            "approved_openings",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(r.state != "draft" or r.approval_state == "pending" for r in self):
            locked |= set(self._FROZEN)
        return locked

    def _compute_fill(self):
        Cand = self.env["fix.candidate"].sudo()
        for rec in self:
            hired = Cand.search_count([("requisition_id", "=", rec.id), ("state", "=", "hired")])
            rec.hired_count = hired
            rec.openings_left = max((rec.approved_openings or rec.openings or 0) - hired, 0)

    @api.constrains("openings")
    def _check_openings(self):
        for rec in self:
            if rec.openings <= 0:
                raise ValidationError("A requisition asks for at least one opening.")

    @api.constrains("assessment_pass_mark")
    def _check_pass_mark(self):
        for rec in self:
            if rec.assessment_pass_mark and not 0 < rec.assessment_pass_mark <= 100:
                raise ValidationError("The assessment pass mark is a percentage above 0.")

    def write(self, vals):
        if not self._fix_guard_open():
            frozen = set(self._FROZEN) & set(vals)
            for rec in self:
                if not frozen or not rec.id:
                    break
                if rec.state != "draft" or rec.approval_state == "pending":
                    changed = [n for n in frozen if rec._fix_guard_differs(n, vals[n], rec[n])]
                    if changed:
                        raise UserError(
                            "%s of %s was approved (or is awaiting approval) and cannot "
                            "change. Raise a new requisition."
                            % (", ".join(self._fields[n].string for n in changed), rec.name)
                        )
        return super().write(vals)

    # ---- transitions ------------------------------------------------------
    def _fix_submit_gate(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft requisition is submitted for approval.")
            if not rec.position_id:
                raise UserError(
                    "Requisition %s names no position. A requisition is raised against an "
                    "established position (BRU-TAO-01)." % rec.name
                )
            if rec.openings <= 0:
                raise UserError("A requisition asks for at least one opening.")
            if rec.is_field_role and not rec.assessment_pass_mark:
                raise UserError(
                    "Field role %s needs a practical assessment pass mark (BRU-TAO-05)." % rec.name
                )

    def action_request_approval(self, justification=None):
        _require_recruiter(self.env, "submit a requisition")
        self._fix_submit_gate()
        return super().action_request_approval(justification=justification)

    def action_approve(self):
        """Routed apply method: the approver opens the requisition."""
        self._approval_assert_routed()
        self._people_assert_not_conflicted()
        self._fix_submit_gate()
        for rec in self:
            rec._guarded().write(
                {
                    "state": "open",
                    "approved_by_id": rec._people_decider().id,
                    "approved_on": fields.Datetime.now(),
                    "approved_openings": rec.openings,
                }
            )
        return True

    def action_close(self):
        _require_recruiter(self.env, "close a requisition")
        for rec in self:
            if rec.state not in ("open", "hired"):
                raise UserError("Only an open or filled requisition is closed.")
            rec._guarded().write({"state": "closed"})
        return True

    def _fix_refresh_fill(self):
        """Filled when the hires reach the approved headcount (M58-F10)."""
        self.invalidate_recordset(["hired_count", "openings_left"])
        for rec in self:
            if rec.state == "open" and rec.openings_left <= 0:
                rec._guarded().write({"state": "hired"})


class FixCandidate(models.Model):
    _name = "fix.candidate"
    _description = "Candidate"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    email = fields.Char()
    phone = fields.Char()
    requisition_id = fields.Many2one("fix.job.requisition", string="Requisition")
    employee_id = fields.Many2one("hr.employee", string="Hired Employee Record", readonly=True)
    source = fields.Selection(
        [
            ("direct", "Direct Application"),
            ("referral", "Employee Referral"),
            ("job_portal", "Job Portal"),
            ("campus", "Campus"),
            ("agency", "Agency"),
            ("internal", "Internal"),
        ],
        string="Source / Channel",
        default="direct",
    )
    date_of_birth = fields.Date(help="Verified before offer: BLA 2006 s.34 (BRU-TAO-17).")
    nid_number = fields.Char(
        string="NID Number", help="10-, 13- or 17-digit National ID. Used to de-duplicate."
    )
    consent_given = fields.Boolean(
        string="Consent to Processing & Retention",
        help="The candidate's consent to process and keep their data (BRU-TAO-13).",
    )
    consent_date = fields.Datetime(readonly=True, copy=False)
    retention_until = fields.Date(
        string="Retain Until",
        readonly=True,
        copy=False,
        help="Set when the candidate is not hired; the retention cron anonymises the "
        "record after this date (BRU-TAO-14).",
    )
    erased = fields.Boolean(string="Anonymised", readonly=True, copy=False)
    rejection_reason = fields.Text(readonly=True, copy=False)
    rejected_on = fields.Datetime(readonly=True, copy=False)
    hired_on = fields.Datetime(readonly=True, copy=False)
    state = fields.Selection(
        [
            ("applied", "Applied"),
            ("screening", "Screening"),
            ("interview", "Interview"),
            ("offered", "Offered"),
            ("hired", "Hired"),
            ("rejected", "Rejected"),
        ],
        default="applied",
        required=True,
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "employee_id",
            "consent_date",
            "retention_until",
            "erased",
            "rejection_reason",
            "rejected_on",
            "hired_on",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(r.state in ("offered", "hired", "rejected") for r in self):
            locked |= {"requisition_id", "date_of_birth", "nid_number"}
        return locked

    # ---- validation and de-duplication -------------------------------------
    @api.constrains("nid_number")
    def _check_nid(self):
        for rec in self:
            nid = (rec.nid_number or "").strip()
            if nid and (not nid.isdigit() or len(nid) not in (10, 13, 17)):
                raise ValidationError("An NID number is 10, 13 or 17 digits.")

    def _fix_identity_domain(self):
        """Candidates that are the same person (email, phone or NID)."""
        self.ensure_one()
        keys = []
        if self.email:
            keys.append(("email", "=ilike", self.email.strip()))
        if _digits(self.phone):
            keys.append(("phone", "ilike", _digits(self.phone)[-10:]))
        if self.nid_number:
            keys.append(("nid_number", "=", self.nid_number.strip()))
        if not keys:
            return None
        return ["|"] * (len(keys) - 1) + keys

    @api.constrains("email", "phone", "nid_number", "requisition_id")
    def _check_duplicate_application(self):
        """AUT-TAO-03: one live application per person and requisition."""
        for rec in self:
            ident = rec._fix_identity_domain()
            if not ident or not rec.requisition_id:
                continue
            dup = (
                self.sudo()
                .with_context(active_test=False)
                .search(
                    [
                        ("id", "!=", rec.id),
                        ("requisition_id", "=", rec.requisition_id.id),
                        ("state", "!=", "rejected"),
                        *ident,
                    ],
                    limit=1,
                )
            )
            if dup:
                raise ValidationError(
                    "%s has already applied to %s (%s): the same email, phone or NID."
                    % (rec.name, rec.requisition_id.name, dup.name)
                )

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        # consent_date is the system's stamp, never typed
        recs.filtered("consent_given")._guarded().write({"consent_date": fields.Datetime.now()})
        return recs

    def write(self, vals):
        if not self._fix_guard_open() and "requisition_id" in vals:
            for rec in self:
                if (
                    rec.id
                    and rec.state in ("offered", "hired", "rejected")
                    and rec._fix_guard_differs(
                        "requisition_id", vals["requisition_id"], rec.requisition_id
                    )
                ):
                    raise UserError(
                        "%s is past the interview; their requisition no longer changes." % rec.name
                    )
        result = super().write(vals)
        if "consent_given" in vals:
            for rec in self:
                if not rec.id:
                    continue
                if rec.consent_given and not rec.consent_date:
                    rec._guarded().write({"consent_date": fields.Datetime.now()})
                elif not rec.consent_given and rec.state not in ("hired",):
                    # consent withdrawn: the record is erased at the next run
                    rec._guarded().write({"retention_until": fields.Date.context_today(rec)})
        return result

    # ---- the gates -----------------------------------------------------------
    def _fix_interview_problems(self):
        self.ensure_one()
        done = (
            self.env["fix.talent.interview"]
            .sudo()
            .search([("candidate_id", "=", self.id), ("state", "=", "done")])
        )
        problems = []
        if not done.filtered(lambda i: i.recommendation in POSITIVE):
            problems.append("no completed interview recommends the hire")
        if done.filtered(lambda i: i.recommendation == "strong_no"):
            problems.append("a completed interview says Strong No")
        return problems

    def _fix_assessment_problems(self):
        self.ensure_one()
        assessments = (
            self.env["fix.talent.assessment"].sudo().search([("candidate_id", "=", self.id)])
        )
        problems = []
        if assessments.filtered(lambda a: not a.passed):
            problems.append("a practical assessment was failed")
        if self.requisition_id.is_field_role and not assessments.filtered("passed"):
            problems.append("a field role needs a passed practical assessment (BRU-TAO-05)")
        return problems

    def _fix_age_problems(self, on_date):
        self.ensure_one()
        minimum = _int_param(self.env, "cd_talent.minimum_hiring_age", 14)
        if not self.date_of_birth:
            return ["no verified date of birth (BRU-TAO-17)"]
        on_date = fields.Date.to_date(on_date) or fields.Date.context_today(self)
        dob = self.date_of_birth
        age = on_date.year - dob.year - ((on_date.month, on_date.day) < (dob.month, dob.day))
        if age < minimum:
            return [
                "the candidate is %d, below the minimum hiring age of %d (BLA 2006 s.34)"
                % (age, minimum)
            ]
        return []

    def _fix_requisition_problems(self):
        self.ensure_one()
        req = self.requisition_id
        if not req:
            return ["no requisition (a hire is made against an approved requisition)"]
        problems = []
        # the fill is counted, never cached across hires in one transaction
        req.invalidate_recordset(["hired_count", "openings_left"])
        if req.state != "open" or req.approval_state != "approved":
            problems.append("requisition %s is not open and approved" % req.name)
        elif req.openings_left <= 0:
            problems.append("requisition %s has no openings left" % req.name)
        return problems

    def _fix_check_problems(self):
        self.ensure_one()
        checks = self.env["fix.talent.check"].sudo().search([("candidate_id", "=", self.id)])
        problems = []
        if checks.filtered(lambda c: c.result != "clear"):
            problems.append("a background check is pending, failed or shows a discrepancy")
        required = REQUIRED_CHECKS + (
            FIELD_ROLE_CHECKS if self.requisition_id.is_field_role else ()
        )
        labels = dict(self.env["fix.talent.check"]._fields["check_type"].selection)
        for kind in required:
            if not checks.filtered(
                lambda c, k=kind: c.check_type == k and c.result == "clear" and c.verified_by_id
            ):
                problems.append("no verified %s check" % labels[kind])
        return problems

    def _fix_duplicate_hire(self):
        self.ensure_one()
        ident = self._fix_identity_domain()
        if not ident:
            return self.browse()
        return (
            self.sudo()
            .with_context(active_test=False)
            .search([("id", "!=", self.id), ("state", "=", "hired"), *ident], limit=1)
        )

    def _fix_hire_problems(self, offer):
        self.ensure_one()
        if self.state == "rejected":
            return ["the candidate was rejected"]
        if self.state == "hired":
            return ["the candidate is already hired"]
        problems = []
        if self.state != "offered":
            problems.append("the candidate has not reached the offer stage")
        problems += self._fix_requisition_problems()
        if not offer or offer.state != "accepted" or offer.candidate_id != self:
            problems.append("no accepted offer")
        problems += self._fix_interview_problems()
        problems += self._fix_check_problems()
        problems += self._fix_assessment_problems()
        if not self.consent_given:
            problems.append("no recorded consent to processing (BRU-TAO-13)")
        problems += self._fix_age_problems(offer.joining_date if offer else None)
        dup = self._fix_duplicate_hire()
        if dup:
            problems.append("the same person is already hired as %s" % dup.name)
        return problems

    # ---- transitions ---------------------------------------------------------
    def _fix_move(self, frm, to, what):
        _require_recruiter(self.env, what)
        for rec in self:
            if rec.state not in frm:
                raise UserError(
                    "%s is %s; %s needs %s."
                    % (
                        rec.name,
                        dict(self._fields["state"].selection)[rec.state],
                        what,
                        " or ".join(dict(self._fields["state"].selection)[s] for s in frm),
                    )
                )
            rec._guarded().write({"state": to})

    def action_screen(self):
        for rec in self:
            if not rec.consent_given:
                raise UserError(
                    "Record %s's consent to processing before screening (BRU-TAO-13)." % rec.name
                )
            problems = rec._fix_requisition_problems()
            if problems:
                raise UserError("Cannot screen %s: %s." % (rec.name, "; ".join(problems)))
        self._fix_move(("applied",), "screening", "screening")
        return True

    def action_interview(self):
        self._fix_move(("screening",), "interview", "an interview invitation")
        return True

    def action_offer(self):
        for rec in self:
            problems = rec._fix_interview_problems() + rec._fix_assessment_problems()
            if problems:
                raise UserError(
                    "%s cannot move to the offer stage: %s." % (rec.name, "; ".join(problems))
                )
        self._fix_move(("interview",), "offered", "the offer stage")
        return True

    def action_reject(self, reason=None):
        """Close the application with its outcome (BRU-TAO-16)."""
        _require_recruiter(self.env, "reject a candidate")
        if not (reason or "").strip():
            raise UserError("State the outcome communicated to the candidate.")
        days = _int_param(self.env, "cd_talent.candidate_retention_days", 0)
        for rec in self:
            if rec.state in ("hired", "rejected"):
                raise UserError("%s is already %s." % (rec.name, rec.state))
            vals = {
                "state": "rejected",
                "rejection_reason": reason.strip(),
                "rejected_on": fields.Datetime.now(),
            }
            if days:
                vals["retention_until"] = fields.Date.context_today(rec) + timedelta(days=days)
            rec._guarded().write(vals)
            rec.message_post(body="Application closed. Outcome communicated: %s" % reason.strip())
        return True

    def action_hire(self, offer=None):
        """Hire from an accepted offer (called by fix.talent.offer.action_accept)."""
        _require_recruiter(self.env, "complete a hire")
        for rec in self:
            accepted = offer or self.env["fix.talent.offer"].sudo().search(
                [("candidate_id", "=", rec.id), ("state", "=", "accepted")], limit=1
            )
            accepted = accepted.sudo()
            problems = rec._fix_hire_problems(accepted)
            if problems:
                raise UserError(
                    "Hiring Gate Blocked (RAP-M58-05) for %s: %s." % (rec.name, "; ".join(problems))
                )
            emp = rec._fix_create_employee(accepted)
            contract = rec._fix_create_contract(emp, accepted)
            rec._guarded().write(
                {"state": "hired", "employee_id": emp.id, "hired_on": fields.Datetime.now()}
            )
            rec._fix_open_onboarding(emp, contract, accepted)
            rec.requisition_id.sudo()._fix_refresh_fill()
        return True

    # ---- the hand-off to M21 (I6) ---------------------------------------------
    def _fix_create_employee(self, offer):
        """The employee master, from verified candidate data and the offer.

        Created with sudo: the Recruitment Officer holds no hr.employee create
        (the master is HR's), and the gates above have run. The joiner event
        is held until onboarding completes (M58-F6)."""
        self.ensure_one()
        req = self.requisition_id
        Employee = hold_joiner(self.env["hr.employee"].sudo().env)["hr.employee"]
        vals = {
            "name": self.name,
            "work_email": self.email or False,
            "work_phone": self.phone or False,
            "company_id": self.company_id.id,
            "operating_unit_id": self.operating_unit_id.id or False,
            "department_id": req.department_id.id or False,
            "position_id": (offer.position_id or req.position_id).id or False,
            "joining_date": offer.joining_date,
            "joined_date": offer.joining_date,
        }
        if self.date_of_birth and "birthday" in Employee._fields:
            vals["birthday"] = self.date_of_birth
        if self.nid_number and "nid_number" in Employee._fields:
            vals["nid_number"] = self.nid_number
        return Employee.create(vals)

    def _fix_create_contract(self, employee, offer):
        """I6: a DRAFT employment contract carrying the offer's salary and date."""
        self.ensure_one()
        basic = offer.basic_salary
        return (
            self.env["fix.employment.contract"]
            .sudo()
            .create(
                {
                    "employee_id": employee.id,
                    "company_id": self.company_id.id,
                    "operating_unit_id": self.operating_unit_id.id or False,
                    "contract_type": offer.contract_type or "probation",
                    "joining_date": offer.joining_date,
                    "basic_monthly": basic,
                    "other_allowance": max((offer.gross_salary or 0.0) - basic, 0.0),
                    "currency_id": offer.currency_id.id,
                }
            )
        )

    def _fix_open_onboarding(self, employee, contract, offer):
        self.ensure_one()
        Plan = self.env["fix.onboarding.plan"].sudo()
        plan = Plan.search([("candidate_id", "=", self.id)], limit=1)
        vals = {
            "employee_id": employee.id,
            "contract_id": contract.id,
            "offer_id": offer.id,
            "joined_date": offer.joining_date,
        }
        if plan:
            plan._guarded().write(vals)
            return plan
        req = self.requisition_id
        return Plan._guarded().create(
            {
                "name": "Onboarding: %s" % self.name,
                "candidate_id": self.id,
                "requisition_id": req.id,
                "position_id": (offer.position_id or req.position_id).id or False,
                "department_id": req.department_id.id or False,
                "company_id": self.company_id.id,
                "operating_unit_id": self.operating_unit_id.id or False,
                **vals,
            }
        )

    # ---- retention (BRU-TAO-14, AUT-TAO-16) -------------------------------------
    @api.model
    def cron_erase_expired_candidates(self):
        """Anonymise candidates past their retention date. Idempotent; superuser."""
        today = fields.Date.context_today(self)
        due = (
            self.sudo()
            .with_context(active_test=False)
            .search(
                [
                    ("retention_until", "!=", False),
                    ("retention_until", "<", today),
                    ("erased", "=", False),
                    ("state", "!=", "hired"),
                ]
            )
        )
        for rec in due:
            rec._guarded().write(
                {
                    "name": "Erased candidate %d" % rec.id,
                    "email": False,
                    "phone": False,
                    "nid_number": False,
                    "date_of_birth": False,
                    "rejection_reason": False,
                    "erased": True,
                }
            )
            self.env["fix.talent.interview"].sudo().search([("candidate_id", "=", rec.id)]).write(
                {"notes": False}
            )
            checks = self.env["fix.talent.check"].sudo().search([("candidate_id", "=", rec.id)])
            checks.write({"notes": False, "reference_contact": False})
            checks._guarded().write({"evidence_file": False})
            rec.message_ids.sudo().unlink()
        return len(due)


class FixOnboardingPlan(models.Model):
    """M58 / MV-01: onboarding. Completion publishes the authoritative
    'employee.joined' for the employee master, which M29 provisions from."""

    _name = "fix.onboarding.plan"
    _description = "Employee Onboarding Plan"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    candidate_id = fields.Many2one("fix.candidate", string="Candidate", required=True)
    requisition_id = fields.Many2one("fix.job.requisition", string="Job Requisition")
    employee_id = fields.Many2one("hr.employee", string="Created Employee Record", readonly=True)
    contract_id = fields.Many2one(
        "fix.employment.contract", string="Draft Employment Contract", readonly=True
    )
    offer_id = fields.Many2one("fix.talent.offer", string="Accepted Offer", readonly=True)
    position_id = fields.Many2one("fix.org.position", string="Position")
    department_id = fields.Many2one("hr.department", string="Department")
    joined_date = fields.Date(string="Joining Date", default=fields.Date.today, required=True)

    # Evidence, not ticks (M58-F8): each prerequisite is read from the record
    # that proves it.
    nid_verified = fields.Boolean(
        string="NID / Identity Verified",
        compute="_compute_evidence",
        help="An NID check on the candidate, cleared by a verifier other than its requester.",
    )
    signed_contract_file = fields.Binary(
        string="Signed Appointment Letter / Contract", attachment=True, copy=False
    )
    signed_contract_filename = fields.Char(copy=False)
    contract_signed = fields.Boolean(
        string="Employment Contract Executed",
        compute="_compute_evidence",
        help="BLA 2006 s.5: the signed appointment letter is on file and the draft "
        "contract exists.",
    )
    bank_details_captured = fields.Boolean(
        string="Payroll & BEFTN Bank Details Captured",
        compute="_compute_evidence",
        help="The employee master holds a bank account and routing number, or an MFS wallet.",
    )
    keycloak_provisioned = fields.Boolean(
        string="Keycloak Identity Provisioned",
        compute="_compute_evidence",
        help="Set by M29 after onboarding completes (the employee has a Keycloak user).",
    )
    safety_kit_issued = fields.Boolean(
        string="PPE Issued & Acknowledged",
        compute="_compute_evidence",
        help="M59: the employee acknowledged a PPE issue. Required for field roles (BRU-TAO-11).",
    )
    it_assets_allocated = fields.Boolean(
        string="IT Equipment & Assets Allocated",
        default=False,
        tracking=True,
        help="Informational: M17 asset hand-over is not linked yet, so this gates nothing.",
    )
    completed_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    completed_on = fields.Datetime(readonly=True, copy=False)
    readiness_escalated_on = fields.Datetime(readonly=True, copy=False)

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "employee_id",
            "contract_id",
            "offer_id",
            "completed_by_id",
            "completed_on",
            "readiness_escalated_on",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(r.state in ("completed", "cancelled") for r in self):
            locked |= {"signed_contract_file", "signed_contract_filename", "joined_date"}
        return locked

    def write(self, vals):
        if not self._fix_guard_open() and {"signed_contract_file", "joined_date"} & set(vals):
            for rec in self:
                if rec.id and rec.state in ("completed", "cancelled"):
                    raise UserError("%s is %s; its evidence is frozen." % (rec.name, rec.state))
        return super().write(vals)

    _EVIDENCE = (
        "nid_verified",
        "contract_signed",
        "bank_details_captured",
        "keycloak_provisioned",
        "safety_kit_issued",
    )

    @api.depends("signed_contract_file", "contract_id", "employee_id", "candidate_id")
    def _compute_evidence(self):
        Check = self.env["fix.talent.check"].sudo()
        Issue = self.env["fix.ppe.issue"].sudo() if "fix.ppe.issue" in self.env else None
        for rec in self:
            emp = rec.employee_id.sudo()
            rec.nid_verified = bool(
                rec.candidate_id
                and Check.search_count(
                    [
                        ("candidate_id", "=", rec.candidate_id.id),
                        ("check_type", "=", "nid"),
                        ("result", "=", "clear"),
                        ("verified_by_id", "!=", False),
                    ]
                )
            )
            rec.contract_signed = bool(rec.signed_contract_file and rec.contract_id)
            rec.bank_details_captured = bool(
                emp and ((emp.bank_account_number and emp.routing_number) or emp.mfs_account_number)
            )
            rec.keycloak_provisioned = bool(emp and emp.keycloak_user_id)
            rec.safety_kit_issued = bool(
                emp
                and Issue is not None
                and Issue.search_count([("employee_id", "=", emp.id), ("acknowledged", "=", True)])
            )

    def _fix_completion_problems(self):
        self.ensure_one()
        # the evidence lives on other records: read it now, not from cache
        self.invalidate_recordset(list(self._EVIDENCE))
        problems = []
        if not self.employee_id or self.candidate_id.state != "hired":
            problems.append("the candidate has not been hired")
        if not self.nid_verified:
            problems.append("NID not verified by a verifier")
        if not self.contract_signed:
            problems.append("no signed appointment letter / contract on file (BLA s.5)")
        if not self.bank_details_captured:
            problems.append("no bank account and routing number, or MFS wallet, on the employee")
        if self.employee_id and not self.employee_id.sudo().employee_code:
            problems.append("the employee has no employee code (M29 keys the identity on it)")
        if self.requisition_id.is_field_role and not self.safety_kit_issued:
            problems.append("a field role needs its PPE issued and acknowledged (BRU-TAO-11)")
        return problems

    def action_start(self):
        _require_recruiter(self.env, "start onboarding")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Start a draft onboarding plan.")
            if not rec.employee_id:
                raise UserError("Onboarding starts after the hire creates the employee.")
            rec._guarded().write({"state": "in_progress"})
        return True

    def action_complete(self):
        _require_recruiter(self.env, "complete onboarding")
        for rec in self:
            if rec.state != "in_progress":
                raise UserError("Complete an onboarding plan that is in progress.")
            problems = rec._fix_completion_problems()
            if problems:
                raise UserError(
                    "Cannot complete onboarding for %s: %s." % (rec.name, "; ".join(problems))
                )
            rec._guarded().write(
                {
                    "state": "completed",
                    "completed_by_id": self.env.user.id,
                    "completed_on": fields.Datetime.now(),
                }
            )
            emp = rec.employee_id.sudo()
            # The one joiner event, on the employee master, carrying what
            # M29 provisions from (M58-F6, M58-33).
            emp._emit_jml("employee.joined", emp._fix_joiner_payload())
        return True

    @api.model
    def cron_escalate_day_one_readiness(self):
        """AUT-TAO-11: N days before the start date, escalate every plan that
        is not complete. Idempotent (stamped once); superuser."""
        lead = _int_param(self.env, "cd_talent.readiness_lead_days", 7)
        horizon = fields.Date.context_today(self) + timedelta(days=lead)
        plans = self.sudo().search(
            [
                ("state", "in", ("draft", "in_progress")),
                ("joined_date", "<=", horizon),
                ("readiness_escalated_on", "=", False),
            ]
        )
        managers = (
            self.env.ref("hr.group_hr_manager")
            .sudo()
            .all_user_ids.filtered(lambda u: u.active and not u.share)
        )
        for plan in plans:
            problems = plan._fix_completion_problems()
            note = "Day-one readiness incomplete %s before the start date %s: %s." % (
                "%d day(s)" % lead,
                plan.joined_date,
                "; ".join(problems) or "plan not completed",
            )
            for user in managers.filtered(lambda u, p=plan: p.company_id in u.company_ids):
                plan.activity_schedule(
                    "mail.mail_activity_data_todo",
                    date_deadline=plan.joined_date,
                    summary="Day-one readiness: %s" % plan.name,
                    note=note,
                    user_id=user.id,
                )
            plan.message_post(body=note)
            plan._guarded().write({"readiness_escalated_on": fields.Datetime.now()})
        return len(plans)
