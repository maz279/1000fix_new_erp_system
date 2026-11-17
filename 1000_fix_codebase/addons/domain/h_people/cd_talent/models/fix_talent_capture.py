# fix_talent_capture — M58 capture audit (2026-11-17).
#
# The M58 sub-module pages listed records nobody could capture, and the spec
# (M58 §5, §10.1) names records the module never had:
#   * job profile (FR-TAO-004): responsibilities, M22 competencies,
#     qualifications, experience and the M57 band, named on the requisition;
#   * job posting (FR-TAO-005/006, BRU-TAO-02, AUT-TAO-02): "Job Postings"
#     listed requisitions; a posting is published only for an open, approved
#     requisition, and an external posting only after the internal
#     consideration window of an internal one;
#   * recruitment channel and cost (FR-TAO-008, FR-TAO-034 cost per hire);
#   * employee referral (FR-TAO-007, AUT-TAO-17): the reward is approved by an
#     HR manager who neither recorded the referral nor made it, after the hire;
#   * pre-boarding documents (FR-TAO-023/024, T-08): the checklist is issued at
#     hire, each document is verified by a Background Verifier who did not
#     upload it, its SHA-256 is kept, and onboarding completes only when every
#     mandatory document is verified;
#   * induction sessions (FR-TAO-029): recorded attended or missed by their
#     conductor (never the new hire), after the session starts; a session
#     still unrecorded holds the onboarding open;
# and the existing records gain what their pages are about: the practical
# assessment's tasks and evidence (FR-TAO-016), the offer's probation and
# benefits (FR-TAO-020, BLA s.4(8)), the onboarding mentor (FR-TAO-031) and
# task dependencies (FR-TAO-027, T-07).
import base64
import hashlib

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from .fix_onboarding_task import guard_first
from .fix_talent import FixJobRequisition, _int_param, _param, _require_recruiter
from .fix_talent_ops import FixTalentOffer

VERIFIER = "cd_talent.group_background_verifier"
HR_MANAGER = "hr.group_hr_manager"

DOCUMENT_TYPES = [
    ("nid", "National ID (NID)"),
    ("photo", "Photograph"),
    ("academic", "Academic Certificates"),
    ("experience", "Experience / Release Letters"),
    ("bank", "Bank / MFS Account Proof"),
    ("age_proof", "Birth Certificate / Age Proof"),
    ("medical", "Medical Fitness"),
    ("other", "Other"),
]
DEFAULT_DOCUMENTS = "nid,photo,academic,experience,bank"

PROBATION_CLASSES = [
    ("clerical", "Clerical (6 months)"),
    ("skilled", "Skilled (3 months, extendable by 3)"),
    ("other", "Other (3 months)"),
]
# BLA 2006 s.4(8), the same caps as the M21 contract (cd_hr_core)
PROBATION_CAP = {"clerical": 6, "skilled": 3, "other": 3}


def _sequence(env, code, fallback):
    return env["ir.sequence"].sudo().next_by_code(code) or fallback


def _require_group(env, xmlid, what):
    if not (env.su or env.user.has_group(xmlid)):
        raise AccessError("Only %s may %s." % (env.ref(xmlid).sudo().name, what))


# =========================================================== job profile
class FixJobProfile(models.Model):
    """What a role asks for (FR-TAO-004). M58 keeps it; the position stays M21's."""

    _name = "fix.job.profile"
    _description = "Job Profile"
    _inherit = ["mail.thread"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    position_id = fields.Many2one(
        "fix.org.position", string="Position (M21)", index=True, tracking=True
    )
    responsibilities = fields.Text(required=True)
    competency_ids = fields.Many2many(
        "fix.competency", string="Required Competencies (M22)", tracking=True
    )
    qualifications = fields.Text(string="Qualifications")
    min_experience_years = fields.Integer(string="Minimum Experience (years)")
    band_id = fields.Many2one("fix.compensation.band", string="Pay Band (M57)")
    active = fields.Boolean(default=True)

    @api.constrains("min_experience_years")
    def _check_experience(self):
        for rec in self:
            if rec.min_experience_years < 0:
                raise ValidationError("Experience is a number of years, zero or more.")

    @api.model_create_multi
    def create(self, vals_list):
        _require_recruiter(self.env, "maintain job profiles")
        return super().create(vals_list)

    def write(self, vals):
        _require_recruiter(self.env, "maintain job profiles")
        return super().write(vals)


class FixJobRequisitionProfile(models.Model):
    _inherit = "fix.job.requisition"

    # the approval covers the profile too
    _FROZEN = (*FixJobRequisition._FROZEN, "job_profile_id")

    job_profile_id = fields.Many2one("fix.job.profile", string="Job Profile")
    posting_ids = fields.One2many("fix.job.posting", "requisition_id", string="Postings")

    @api.constrains("job_profile_id", "position_id")
    def _check_profile_position(self):
        for rec in self:
            prof = rec.job_profile_id.sudo()
            if prof.position_id and rec.position_id and prof.position_id != rec.position_id:
                raise ValidationError(
                    "Job profile %s is for position %s, not %s."
                    % (prof.name, prof.position_id.name, rec.position_id.name)
                )


# =========================================================== channels and cost
class FixRecruitmentChannel(models.Model):
    """A sourcing channel or agency, with its cost model (FR-TAO-008)."""

    _name = "fix.recruitment.channel"
    _description = "Recruitment Channel"
    _inherit = ["mail.thread"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    channel_type = fields.Selection(
        [
            ("job_portal", "Job Portal"),
            ("agency", "Recruitment Agency"),
            ("social", "Social Media"),
            ("newspaper", "Newspaper"),
            ("campus", "Campus"),
            ("referral", "Employee Referral"),
            ("internal", "Internal"),
            ("other", "Other"),
        ],
        required=True,
        default="job_portal",
    )
    partner_id = fields.Many2one("res.partner", string="Agency / Provider")
    cost_model = fields.Selection(
        [
            ("free", "No Cost"),
            ("fixed", "Fixed Fee (period)"),
            ("per_posting", "Per Posting"),
            ("per_hire", "Per Hire"),
        ],
        required=True,
        default="free",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.company.currency_id
    )
    fee = fields.Monetary(currency_field="currency_id", string="Agreed Fee")
    contract_ref = fields.Char(string="Contract Reference")
    active = fields.Boolean(default=True)

    @api.constrains("channel_type", "partner_id", "cost_model", "fee")
    def _check_channel(self):
        for rec in self:
            if rec.channel_type == "agency" and not rec.partner_id:
                raise ValidationError("An agency channel names the agency.")
            if (rec.fee or 0.0) < 0:
                raise ValidationError("A fee is not negative.")
            if rec.cost_model != "free" and (rec.fee or 0.0) <= 0:
                raise ValidationError(
                    "Channel %s charges (%s): record the agreed fee."
                    % (rec.name, dict(self._fields["cost_model"].selection)[rec.cost_model])
                )

    @api.model_create_multi
    def create(self, vals_list):
        _require_recruiter(self.env, "maintain recruitment channels")
        return super().create(vals_list)

    def write(self, vals):
        _require_recruiter(self.env, "maintain recruitment channels")
        return super().write(vals)


class FixRecruitmentCost(models.Model):
    """A cost incurred for a requisition (cost per hire, FR-TAO-034)."""

    _name = "fix.recruitment.cost"
    _description = "Recruitment Cost"
    _order = "incurred_on desc, id desc"

    name = fields.Char(required=True, default="New", copy=False)
    requisition_id = fields.Many2one(
        "fix.job.requisition", required=True, index=True, ondelete="restrict"
    )
    company_id = fields.Many2one(
        related="requisition_id.company_id", store=True, index=True, string="Company"
    )
    operating_unit_id = fields.Many2one(
        related="requisition_id.operating_unit_id", store=True, string="Operating Unit"
    )
    channel_id = fields.Many2one("fix.recruitment.channel", string="Channel / Agency")
    cost_type = fields.Selection(
        [
            ("advertising", "Advertising / Posting"),
            ("agency_fee", "Agency Fee"),
            ("assessment", "Assessment"),
            ("background_check", "Background / Police Check"),
            ("travel", "Candidate Travel"),
            ("other", "Other"),
        ],
        required=True,
        default="advertising",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.company.currency_id
    )
    amount = fields.Monetary(currency_field="currency_id", required=True)
    incurred_on = fields.Date(required=True, default=fields.Date.context_today)
    invoice_ref = fields.Char(string="Invoice / Bill Reference")
    notes = fields.Text()

    @api.constrains("amount", "requisition_id", "cost_type", "channel_id")
    def _check_cost(self):
        for rec in self:
            if (rec.amount or 0.0) <= 0:
                raise ValidationError("A recruitment cost is a positive amount.")
            if rec.requisition_id.sudo().state == "draft":
                raise ValidationError(
                    "Requisition %s is not approved: no recruitment spend before approval "
                    "(BRU-TAO-02)." % rec.requisition_id.sudo().name
                )
            if rec.cost_type == "agency_fee" and not rec.channel_id:
                raise ValidationError("An agency fee names the agency's channel.")

    @api.model_create_multi
    def create(self, vals_list):
        _require_recruiter(self.env, "record recruitment costs")
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = _sequence(self.env, "fix.recruitment.cost", "RCOST/New")
        return super().create(vals_list)

    def write(self, vals):
        _require_recruiter(self.env, "record recruitment costs")
        return super().write(vals)


# =========================================================== job posting
class FixJobPosting(models.Model):
    """A published opening (FR-TAO-005). Internal first where policy says so
    (FR-TAO-006, AUT-TAO-02)."""

    _name = "fix.job.posting"
    _description = "Job Posting"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    _LOCKED = ("requisition_id", "audience", "channel_id", "title", "description")

    name = fields.Char(required=True, default="New", copy=False)
    title = fields.Char(required=True, tracking=True)
    requisition_id = fields.Many2one(
        "fix.job.requisition", required=True, index=True, ondelete="restrict"
    )
    company_id = fields.Many2one(
        related="requisition_id.company_id", store=True, index=True, string="Company"
    )
    operating_unit_id = fields.Many2one(
        related="requisition_id.operating_unit_id", store=True, string="Operating Unit"
    )
    audience = fields.Selection(
        [("internal", "Internal (employees)"), ("external", "External")],
        required=True,
        default="internal",
        tracking=True,
    )
    channel_id = fields.Many2one("fix.recruitment.channel", string="Channel")
    description = fields.Text()
    closes_on = fields.Date(string="Applications Close")
    published_on = fields.Date(readonly=True, copy=False)
    published_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    internal_only_until = fields.Date(
        string="Internal Only Until",
        readonly=True,
        copy=False,
        help="Set when an internal posting is published: no external posting of the "
        "requisition before this date (internal consideration, FR-TAO-006).",
    )
    candidate_count = fields.Integer(compute="_compute_candidates", string="Applicants")
    state = fields.Selection(
        [("draft", "Draft"), ("published", "Published"), ("closed", "Closed")],
        required=True,
        default="draft",
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "published_on",
            "published_by_id",
            "internal_only_until",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(r.state != "draft" for r in self):
            locked |= set(self._LOCKED)
        return locked

    def _compute_candidates(self):
        Cand = self.env["fix.candidate"].sudo()
        for rec in self:
            rec.candidate_count = Cand.search_count([("posting_id", "=", rec.id)])

    @api.model_create_multi
    def create(self, vals_list):
        _require_recruiter(self.env, "draft job postings")
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = _sequence(self.env, "fix.job.posting", "JPOST/New")
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open():
            guard_first(self, vals)
            _require_recruiter(self.env, "change job postings")
            changed = set(self._LOCKED) & set(vals)
            for rec in self:
                if (
                    rec.id
                    and rec.state != "draft"
                    and changed
                    and any(rec._fix_guard_differs(n, vals[n], rec[n]) for n in changed)
                ):
                    raise UserError(
                        "Posting %s is %s: what was published does not change. Close it "
                        "and post again." % (rec.name, rec.state)
                    )
        return super().write(vals)

    def _fix_window_days(self):
        return _int_param(self.env, "cd_talent.internal_consideration_days", 7)

    def _fix_publish_problems(self):
        self.ensure_one()
        req = self.requisition_id.sudo()
        problems = []
        today = fields.Date.context_today(self)
        if req.state != "open" or req.approval_state != "approved":
            problems.append(
                "requisition %s is not open and approved (BRU-TAO-02: no posting before "
                "approval)" % req.name
            )
        if self.closes_on and self.closes_on < today:
            problems.append("the closing date has passed")
        if self.audience == "external":
            if not self.channel_id:
                problems.append("an external posting names its channel")
            days = self._fix_window_days()
            if days > 0:
                internal = self.sudo().search(
                    [
                        ("requisition_id", "=", req.id),
                        ("audience", "=", "internal"),
                        ("state", "in", ("published", "closed")),
                    ],
                    order="internal_only_until",
                    limit=1,
                )
                if not internal:
                    problems.append(
                        "the opening was not posted internally first (FR-TAO-006: internal "
                        "consideration for %d day(s))" % days
                    )
                elif internal.internal_only_until and internal.internal_only_until > today:
                    problems.append(
                        "the opening is internal only until %s (FR-TAO-006)"
                        % internal.internal_only_until
                    )
        return problems

    def action_publish(self):
        _require_recruiter(self.env, "publish job postings")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Publish a draft posting.")
            problems = rec._fix_publish_problems()
            if problems:
                raise UserError(
                    "Posting %s cannot be published: %s." % (rec.name, "; ".join(problems))
                )
            today = fields.Date.context_today(rec)
            vals = {"state": "published", "published_on": today, "published_by_id": self.env.uid}
            if rec.audience == "internal":
                vals["internal_only_until"] = today + relativedelta(days=rec._fix_window_days())
            rec._guarded().write(vals)
        return True

    def action_close(self):
        _require_recruiter(self.env, "close job postings")
        for rec in self:
            if rec.state != "published":
                raise UserError("Close a published posting.")
            rec._guarded().write({"state": "closed"})
        return True


class FixCandidateSourcing(models.Model):
    _inherit = "fix.candidate"

    posting_id = fields.Many2one("fix.job.posting", string="Applied Through Posting")
    channel_id = fields.Many2one("fix.recruitment.channel", string="Channel / Agency")

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(r.state in ("offered", "hired", "rejected") for r in self):
            locked |= {"posting_id"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("posting_id") and not vals.get("requisition_id"):
                posting = self.env["fix.job.posting"].sudo().browse(vals["posting_id"])
                vals["requisition_id"] = posting.requisition_id.id
        return super().create(vals_list)

    @api.constrains("posting_id", "requisition_id")
    def _check_posting(self):
        for rec in self:
            posting = rec.posting_id.sudo()
            if not posting:
                continue
            if posting.requisition_id != rec.requisition_id:
                raise ValidationError(
                    "Posting %s is for requisition %s, not the candidate's."
                    % (posting.name, posting.requisition_id.name)
                )
            if posting.state == "draft":
                raise ValidationError("Posting %s was never published." % posting.name)

    def action_hire(self, offer=None):
        result = super().action_hire(offer=offer)
        plans = self.env["fix.onboarding.plan"].sudo().search([("candidate_id", "in", self.ids)])
        plans._fix_generate_documents()
        return result


# =========================================================== referral
class FixTalentReferral(models.Model):
    """An employee referral and its reward decision (FR-TAO-007, AUT-TAO-17)."""

    _name = "fix.talent.referral"
    _description = "Employee Referral"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(required=True, default="New", copy=False)
    candidate_id = fields.Many2one("fix.candidate", required=True, index=True, ondelete="cascade")
    company_id = fields.Many2one(
        related="candidate_id.company_id", store=True, index=True, string="Company"
    )
    operating_unit_id = fields.Many2one(
        related="candidate_id.operating_unit_id", store=True, string="Operating Unit"
    )
    requisition_id = fields.Many2one(related="candidate_id.requisition_id", string="Requisition")
    candidate_state = fields.Selection(related="candidate_id.state", string="Outcome")
    referring_employee_id = fields.Many2one(
        "hr.employee", string="Referred By", required=True, index=True
    )
    relationship = fields.Char(string="Relationship to Candidate")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.company.currency_id
    )
    reward_amount = fields.Monetary(currency_field="currency_id", string="Referral Reward")
    reward_state = fields.Selection(
        [
            ("open", "Open"),
            ("approved", "Reward Approved"),
            ("declined", "No Reward"),
        ],
        required=True,
        default="open",
        tracking=True,
    )
    decided_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    decided_on = fields.Datetime(readonly=True, copy=False)
    decision_note = fields.Char(readonly=True, copy=False)

    _one_per_candidate = models.UniqueIndex("(candidate_id)")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "reward_state",
            "decided_by_id",
            "decided_on",
            "decision_note",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(r.reward_state != "open" for r in self):
            locked |= {"candidate_id", "referring_employee_id", "reward_amount", "currency_id"}
        return locked

    @api.constrains("referring_employee_id", "candidate_id", "reward_amount")
    def _check_referral(self):
        for rec in self:
            emp = rec.referring_employee_id.sudo()
            cand = rec.candidate_id.sudo()
            if (rec.reward_amount or 0.0) < 0:
                raise ValidationError("A referral reward is not negative.")
            if cand.employee_id and cand.employee_id == emp:
                raise ValidationError("An employee does not refer themself.")
            emails = {e.strip().lower() for e in (emp.work_email, emp.private_email) if e}
            if cand.email and cand.email.strip().lower() in emails:
                raise ValidationError(
                    "%s carries the referring employee's own email: a self-referral." % cand.name
                )

    @api.model_create_multi
    def create(self, vals_list):
        _require_recruiter(self.env, "record referrals")
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = _sequence(self.env, "fix.talent.referral", "REF/New")
            cand = self.env["fix.candidate"].sudo().browse(vals.get("candidate_id"))
            if cand.exists() and self.sudo().search_count([("candidate_id", "=", cand.id)]):
                raise UserError("%s already has a referral recorded." % cand.name)
        recs = super().create(vals_list)
        for rec in recs:
            cand = rec.candidate_id.sudo()
            if cand.source != "referral" and cand.state not in ("hired", "rejected"):
                cand.write({"source": "referral"})
        return recs

    def write(self, vals):
        if not self._fix_guard_open():
            guard_first(self, vals)
            _require_recruiter(self.env, "change referrals")
            if any(r.reward_state != "open" for r in self) and (
                {"candidate_id", "referring_employee_id", "reward_amount"} & set(vals)
            ):
                for rec in self.filtered(lambda r: r.reward_state != "open"):
                    for n in {"candidate_id", "referring_employee_id", "reward_amount"} & set(vals):
                        if rec._fix_guard_differs(n, vals[n], rec[n]):
                            raise UserError("The reward of %s is decided." % rec.name)
        return super().write(vals)

    def _fix_decider_checks(self):
        _require_group(self.env, HR_MANAGER, "decide referral rewards")
        for rec in self:
            if rec.reward_state != "open":
                raise UserError("The reward of %s is already decided." % rec.name)
            if self.env.su:
                continue
            if rec.create_uid == self.env.user:
                raise UserError("You recorded %s; another HR manager decides it." % rec.name)
            if rec.referring_employee_id.sudo().user_id == self.env.user:
                raise UserError("You made referral %s; you do not decide its reward." % rec.name)

    def action_approve_reward(self):
        """AUT-TAO-17: the reward of a hired referral, approved by an HR
        manager who neither recorded nor made it. Paid by M56 payroll."""
        self._fix_decider_checks()
        for rec in self:
            if rec.candidate_id.sudo().state != "hired":
                raise UserError("%s is not hired: no referral reward." % rec.candidate_id.name)
            if (rec.reward_amount or 0.0) <= 0:
                raise UserError("Record the reward amount of %s first." % rec.name)
            rec._guarded().write(
                {
                    "reward_state": "approved",
                    "decided_by_id": self.env.uid,
                    "decided_on": fields.Datetime.now(),
                }
            )
        return True

    def action_decline_reward(self, reason=None):
        self._fix_decider_checks()
        if not (reason or "").strip():
            raise UserError("Say why no reward is due.")
        for rec in self:
            rec._guarded().write(
                {
                    "reward_state": "declined",
                    "decided_by_id": self.env.uid,
                    "decided_on": fields.Datetime.now(),
                    "decision_note": reason.strip(),
                }
            )
        return True


# =========================================================== pre-boarding documents
class FixPreboardingDocument(models.Model):
    """One required pre-joining document (FR-TAO-023/024, T-08)."""

    _name = "fix.preboarding.document"
    _description = "Pre-Boarding Document"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "plan_id, id"

    name = fields.Char(required=True, default="New", copy=False)
    plan_id = fields.Many2one("fix.onboarding.plan", required=True, index=True, ondelete="cascade")
    company_id = fields.Many2one(
        related="plan_id.company_id", store=True, index=True, string="Company"
    )
    operating_unit_id = fields.Many2one(
        related="plan_id.operating_unit_id", store=True, string="Operating Unit"
    )
    candidate_id = fields.Many2one(related="plan_id.candidate_id", string="Candidate")
    employee_id = fields.Many2one(related="plan_id.employee_id", string="New Hire")
    document_type = fields.Selection(DOCUMENT_TYPES, required=True, default="other")
    mandatory = fields.Boolean(
        default=True,
        help="The onboarding completes only when every mandatory document is verified.",
    )
    document_file = fields.Binary(string="Document", attachment=True, copy=False)
    document_filename = fields.Char(copy=False)
    file_sha256 = fields.Char(string="SHA-256", readonly=True, copy=False)
    uploaded_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    submitted_on = fields.Datetime(readonly=True, copy=False)
    verified_by_id = fields.Many2one("res.users", string="Verified By", readonly=True, copy=False)
    verified_on = fields.Datetime(readonly=True, copy=False)
    rejection_reason = fields.Char(readonly=True, copy=False)
    notes = fields.Text()
    state = fields.Selection(
        [
            ("requested", "Requested"),
            ("submitted", "Submitted"),
            ("verified", "Verified"),
            ("rejected", "Rejected"),
        ],
        required=True,
        default="requested",
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "mandatory",
            "file_sha256",
            "uploaded_by_id",
            "submitted_on",
            "verified_by_id",
            "verified_on",
            "rejection_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(r.state == "verified" for r in self):
            locked |= {"document_file", "document_filename", "document_type", "plan_id"}
        return locked

    def _fix_stamp_upload(self):
        for rec in self:
            if rec.document_file:
                raw = base64.b64decode(rec.with_context(bin_size=False).document_file or b"")
                rec._guarded().write(
                    {
                        "state": "submitted",
                        "file_sha256": hashlib.sha256(raw).hexdigest(),
                        "uploaded_by_id": self.env.uid,
                        "submitted_on": fields.Datetime.now(),
                        "rejection_reason": False,
                    }
                )
            else:
                rec._guarded().write(
                    {"state": "requested", "file_sha256": False, "uploaded_by_id": False}
                )

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            _require_recruiter(self.env, "request pre-boarding documents")
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                label = dict(DOCUMENT_TYPES).get(vals.get("document_type") or "other")
                vals["name"] = label
        plans = (
            self.env["fix.onboarding.plan"]
            .sudo()
            .browse([v.get("plan_id") for v in vals_list if v.get("plan_id")])
        )
        if plans.filtered(lambda p: p.state not in ("draft", "in_progress")):
            raise UserError("The onboarding plan is closed.")
        recs = super().create(vals_list)
        recs.filtered("document_file")._fix_stamp_upload()
        return recs

    def write(self, vals):
        if not self._fix_guard_open():
            guard_first(self, vals)
            _require_recruiter(self.env, "collect pre-boarding documents")
            locked = {"document_file", "document_type", "plan_id"} & set(vals)
            for rec in self:
                if (
                    rec.state == "verified"
                    and locked
                    and any(rec._fix_guard_differs(n, vals[n], rec[n]) for n in locked)
                ):
                    raise UserError("%s is verified; it is a record." % rec.name)
        changed = self.browse()
        if "document_file" in vals and not self._fix_guard_open():
            changed = self.filtered(
                lambda r: r._fix_guard_differs(
                    "document_file", vals["document_file"], r.document_file
                )
            )
        result = super().write(vals)
        changed._fix_stamp_upload()
        return result

    def _fix_verifier_checks(self):
        _require_group(self.env, VERIFIER, "verify pre-boarding documents")
        for rec in self:
            if rec.state != "submitted":
                raise UserError("%s has no submitted document to decide." % rec.name)
            if rec.plan_id.sudo().state not in ("draft", "in_progress"):
                raise UserError("The onboarding plan of %s is closed." % rec.name)
            if self.env.su:
                continue
            if rec.uploaded_by_id == self.env.user:
                raise UserError("You uploaded %s; another verifier decides it." % rec.name)
            if rec.employee_id.sudo().user_id == self.env.user:
                raise UserError("You do not verify your own documents.")

    def action_verify(self):
        """FR-TAO-024: the verifier and the outcome are recorded."""
        self._fix_verifier_checks()
        for rec in self:
            rec._guarded().write(
                {
                    "state": "verified",
                    "verified_by_id": self.env.uid,
                    "verified_on": fields.Datetime.now(),
                }
            )
        return True

    def action_reject(self, reason=None):
        self._fix_verifier_checks()
        if not (reason or "").strip():
            raise UserError("Say what is wrong with the document.")
        for rec in self:
            rec._guarded().write({"state": "rejected", "rejection_reason": reason.strip()})
        return True


# =========================================================== induction
class FixOnboardingInduction(models.Model):
    """An induction session of a new hire (FR-TAO-029)."""

    _name = "fix.onboarding.induction"
    _description = "Induction Session"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "scheduled_at, id"

    name = fields.Char(required=True, default="New", copy=False)
    plan_id = fields.Many2one("fix.onboarding.plan", required=True, index=True, ondelete="cascade")
    company_id = fields.Many2one(
        related="plan_id.company_id", store=True, index=True, string="Company"
    )
    operating_unit_id = fields.Many2one(
        related="plan_id.operating_unit_id", store=True, string="Operating Unit"
    )
    employee_id = fields.Many2one(related="plan_id.employee_id", string="New Hire")
    session_type = fields.Selection(
        [
            ("company", "Company"),
            ("policy", "HR Policy & Code of Conduct"),
            ("safety", "Safety (M59)"),
            ("systems", "Systems & Tools"),
            ("brand", "Brand & Product"),
            ("branch", "Branch / Workshop"),
        ],
        required=True,
        default="company",
    )
    scheduled_at = fields.Datetime(required=True)
    conductor_id = fields.Many2one("res.users", string="Conducted By", required=True, index=True)
    venue = fields.Char()
    outcome_note = fields.Char(readonly=True, copy=False)
    recorded_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    recorded_on = fields.Datetime(readonly=True, copy=False)
    state = fields.Selection(
        [
            ("scheduled", "Scheduled"),
            ("attended", "Attended"),
            ("missed", "Missed"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="scheduled",
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "outcome_note",
            "recorded_by_id",
            "recorded_on",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(r.state != "scheduled" for r in self):
            locked |= {"plan_id", "session_type", "scheduled_at", "conductor_id", "venue"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        _require_recruiter(self.env, "schedule inductions")
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = _sequence(self.env, "fix.onboarding.induction", "IND/New")
        recs = super().create(vals_list)
        if recs.plan_id.filtered(lambda p: p.state not in ("draft", "in_progress")):
            raise UserError("The onboarding plan is closed.")
        return recs

    def write(self, vals):
        if not self._fix_guard_open():
            guard_first(self, vals)
            _require_recruiter(self.env, "reschedule inductions")
            if any(r.state != "scheduled" for r in self):
                raise UserError("A recorded or cancelled induction is a record.")
        return super().write(vals)

    def _fix_record(self, state, note=None):
        for rec in self:
            if not self.env.su and rec.conductor_id != self.env.user:
                raise AccessError("Only %s records %s." % (rec.conductor_id.name, rec.name))
            if not self.env.su and rec.employee_id.sudo().user_id == self.env.user:
                raise AccessError("The new hire does not record their own induction.")
            if rec.state != "scheduled":
                raise UserError("%s is already %s." % (rec.name, rec.state))
            if rec.scheduled_at > fields.Datetime.now():
                raise UserError("%s has not started yet (%s)." % (rec.name, rec.scheduled_at))
            rec._guarded().write(
                {
                    "state": state,
                    "outcome_note": (note or "").strip() or False,
                    "recorded_by_id": self.env.uid,
                    "recorded_on": fields.Datetime.now(),
                }
            )
        return True

    def action_mark_attended(self):
        return self._fix_record("attended")

    def action_mark_missed(self, reason=None):
        if not (reason or "").strip():
            raise UserError("Say why the session was missed.")
        return self._fix_record("missed", reason)

    def action_cancel(self, reason=None):
        _require_recruiter(self.env, "cancel inductions")
        if not (reason or "").strip():
            raise UserError("Say why the session is cancelled.")
        for rec in self:
            if rec.state != "scheduled":
                raise UserError("%s is already %s." % (rec.name, rec.state))
            rec._guarded().write(
                {
                    "state": "cancelled",
                    "outcome_note": reason.strip(),
                    "recorded_by_id": self.env.uid,
                    "recorded_on": fields.Datetime.now(),
                }
            )
        return True


# =========================================================== the onboarding plan
class FixOnboardingPlanCapture(models.Model):
    _inherit = "fix.onboarding.plan"

    document_ids = fields.One2many(
        "fix.preboarding.document", "plan_id", string="Pre-Boarding Documents"
    )
    induction_ids = fields.One2many(
        "fix.onboarding.induction", "plan_id", string="Induction Sessions"
    )
    documents_required = fields.Integer(compute="_compute_documents", string="Mandatory Documents")
    documents_verified = fields.Integer(
        compute="_compute_documents", string="Mandatory Documents Verified"
    )
    mentor_id = fields.Many2one(
        "hr.employee",
        string="Mentor / Buddy",
        tracking=True,
        help="FR-TAO-031: the mentor holds the structured first-90 check-ins.",
    )

    @api.depends("document_ids.state", "document_ids.mandatory")
    def _compute_documents(self):
        for rec in self:
            docs = rec.sudo().document_ids.filtered("mandatory")
            rec.documents_required = len(docs)
            rec.documents_verified = len(docs.filtered(lambda d: d.state == "verified"))

    @api.constrains("mentor_id", "employee_id")
    def _check_mentor(self):
        for rec in self:
            if rec.mentor_id and rec.mentor_id == rec.employee_id:
                raise ValidationError("A new hire is not their own mentor.")

    def _fix_generate_documents(self):
        """The checklist of FR-TAO-023, issued once per plan (idempotent)."""
        raw = _param(self.env, "cd_talent.preboarding_documents", DEFAULT_DOCUMENTS)
        wanted = [t.strip() for t in (raw or "").split(",") if t.strip()]
        known = dict(DOCUMENT_TYPES)
        Doc = self.env["fix.preboarding.document"].sudo()
        for rec in self:
            have = set(rec.sudo().document_ids.mapped("document_type"))
            for kind in wanted:
                if kind in known and kind not in have:
                    Doc._guarded().create(
                        {"plan_id": rec.id, "document_type": kind, "name": known[kind]}
                    )
        return True

    def _fix_completion_problems(self):
        problems = super()._fix_completion_problems()
        docs = self.sudo().document_ids.filtered(lambda d: d.mandatory and d.state != "verified")
        if docs:
            problems.append(
                "%d mandatory pre-boarding document(s) not verified: %s"
                % (len(docs), ", ".join(docs.mapped("name")))
            )
        pending = self.sudo().induction_ids.filtered(lambda i: i.state == "scheduled")
        if pending:
            problems.append(
                "%d induction session(s) not yet recorded: %s"
                % (len(pending), ", ".join(pending.mapped("name")))
            )
        safety = self.sudo().induction_ids.filtered(lambda i: i.session_type == "safety")
        if (
            self.requisition_id.sudo().is_field_role
            and safety
            and not safety.filtered(lambda i: i.state == "attended")
        ):
            problems.append("the field hire did not attend the safety induction (BRU-TAO-11)")
        return problems


# =========================================================== task dependencies
class FixOnboardingTaskDependency(models.Model):
    _inherit = "fix.onboarding.task"

    depends_on_id = fields.Many2one(
        "fix.onboarding.task",
        string="Depends On",
        help="T-07: this task is completed only after the task it depends on is done.",
    )

    def _fix_guarded_fields(self) -> set:
        # The plan is the creator's input, not a workflow stamp: chosen when an
        # ad-hoc task is added (so "+ New" can save it), then fixed (write).
        return super()._fix_guarded_fields() - {"plan_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(r.id for r in self):
            # a task's plan is fixed once it exists
            locked |= {"plan_id"}
        return locked

    def write(self, vals):
        if "plan_id" in vals and not self._fix_guard_open():
            for rec in self:
                if rec.id and rec._fix_guard_differs("plan_id", vals["plan_id"], rec.plan_id):
                    raise UserError(
                        "%s belongs to its onboarding plan; it does not move." % rec.name
                    )
        return super().write(vals)

    @api.constrains("depends_on_id", "plan_id")
    def _check_dependency(self):
        for rec in self:
            dep = rec.depends_on_id
            if not dep:
                continue
            if dep.plan_id != rec.plan_id:
                raise ValidationError("A task depends only on a task of its own plan.")
            seen, node = {rec.id}, dep
            while node:
                if node.id in seen:
                    raise ValidationError("Task dependencies may not loop.")
                seen.add(node.id)
                node = node.depends_on_id

    def action_done(self):
        for rec in self:
            dep = rec.sudo().depends_on_id
            if dep and dep.state == "open":
                raise UserError("%s waits for %s to be done first." % (rec.name, dep.name))
        return super().action_done()


# =========================================================== assessment evidence
class FixTalentAssessmentEvidence(models.Model):
    _inherit = "fix.talent.assessment"

    tasks_performed = fields.Text(
        string="Tasks Performed",
        help="FR-TAO-016: the bench tasks the candidate performed.",
    )
    evidence_file = fields.Binary(string="Assessment Evidence", attachment=True, copy=False)
    evidence_filename = fields.Char(copy=False)

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(r.baseline_id for r in self):
            locked |= {"tasks_performed", "evidence_file", "evidence_filename"}
        return locked

    def write(self, vals):
        frozen = {"tasks_performed", "evidence_file"} & set(vals)
        if frozen and not self._fix_guard_open():
            for rec in self:
                if rec.baseline_id and any(
                    rec._fix_guard_differs(n, vals[n], rec[n]) for n in frozen
                ):
                    raise UserError(
                        "%s is the employee's M22 baseline; its evidence no longer changes."
                        % rec.name
                    )
        return super().write(vals)


# =========================================================== offer probation and benefits
class FixTalentOfferTerms(models.Model):
    _inherit = "fix.talent.offer"

    _TERMS = (*FixTalentOffer._TERMS, "probation_class", "probation_months", "benefits")

    probation_class = fields.Selection(
        PROBATION_CLASSES, string="Probation Class (BLA s.4(8))", default="clerical"
    )
    probation_months = fields.Integer(
        string="Probation (months)",
        default=6,
        help="Carried to the draft contract's probation end. Capped by the class.",
    )
    benefits = fields.Text(string="Benefits")

    @api.constrains("probation_class", "probation_months", "contract_type")
    def _check_probation(self):
        for rec in self:
            months = rec.probation_months or 0
            cap = PROBATION_CAP.get(rec.probation_class or "clerical", 6)
            if months < 0 or months > cap:
                raise ValidationError(
                    "Probation for a %s worker is at most %d months (BLA s.4(8))."
                    % (rec.probation_class or "clerical", cap)
                )

    def _fix_issue_problems(self):
        problems = super()._fix_issue_problems()
        if self.contract_type == "probation" and not self.probation_months:
            problems.append("a probation offer states its probation period (FR-TAO-020)")
        return problems


class FixCandidateContractTerms(models.Model):
    _inherit = "fix.candidate"

    def _fix_create_contract(self, employee, offer):
        contract = super()._fix_create_contract(employee, offer)
        vals = {}
        if offer.probation_class:
            vals["probation_class"] = offer.probation_class
        if offer.contract_type == "probation" and offer.probation_months and offer.joining_date:
            vals["probation_end"] = offer.joining_date + relativedelta(
                months=offer.probation_months, days=-1
            )
        if vals:
            contract.sudo().write(vals)
        return contract


class FixOnboardingPlanLetter(models.Model):
    _inherit = "fix.onboarding.plan"

    def _fix_appointment_text(self):
        text = super()._fix_appointment_text()
        offer = self.offer_id.sudo()
        extra = ""
        if offer.probation_months:
            extra += "Probation period: %d month(s)\n" % offer.probation_months
        if offer.benefits:
            extra += "Benefits: %s\n" % offer.benefits.strip()
        marker = "Generated by the system"
        if extra and marker in text:
            text = text.replace(marker, extra + marker, 1)
        return text
