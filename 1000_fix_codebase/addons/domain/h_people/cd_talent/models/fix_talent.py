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
import base64
import hashlib
import hmac
import secrets
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


# The identity hash shared with M21 (cd_hr_core fix_hr_identity_residency):
# the same key and message, so a candidate's hash and an employee's hash of
# one NID are equal, and neither table holds the NID in clear for long.
IDENTITY_HASH_KEY = "cd_hr_core.identity_hash_key"


def nid_hash(env, value):
    value = str(value or "").strip()
    if not value:
        return False
    key = env["ir.config_parameter"].sudo().get_param(IDENTITY_HASH_KEY)
    if not key:
        # never minted at hash time: a new key silently breaks every duplicate check
        raise UserError("The identity hash key is missing: upgrade the Talent module.")
    return hmac.new(key.encode(), ("nid:%s" % value).encode(), hashlib.sha256).hexdigest()


RECRUITER = "cd_talent.group_talent"
HIRING_MANAGER = "cd_talent.group_hiring_manager"
# BRU-TAO-01 / R03: a requisition beyond the approved headcount budget is
# decided by the CFO tier, like an out-of-band offer.
CFO_GROUP = "cd_entity_config.group_dofa_tier_4"
LIVE_REQ_STATES = ("open",)


def _is_recruiter(env):
    return env.su or env.user.has_group(RECRUITER)


def _require_recruiter(env, what):
    if not _is_recruiter(env):
        raise AccessError("Only Recruitment may %s." % what)


def _require_recruiter_or_hiring_manager(env, requisitions, what):
    """M58-F7: a hiring manager acts on their own requisitions' records only."""
    if _is_recruiter(env):
        return
    if (
        env.user.has_group(HIRING_MANAGER)
        and requisitions
        and all(r.sudo().hiring_manager_id == env.user for r in requisitions)
    ):
        return
    raise AccessError("Only Recruitment, or the requisition's own hiring manager, may %s." % what)


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
        "hiring_manager_id",
        "budget_year",
        "over_budget_reason",
        "onboarding_template_id",
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
    # M58-F7: the hiring manager sees and acts on their own requisitions only.
    hiring_manager_id = fields.Many2one(
        "res.users",
        string="Hiring Manager",
        index=True,
        default=lambda self: self._default_hiring_manager(),
        help="The manager this requisition hires for. A Hiring Manager reads and works only "
        "the requisitions, candidates and onboarding plans that name them.",
    )
    # BRU-TAO-01: the approved headcount budget for the position or department.
    budget_year = fields.Integer(
        string="Budget Year",
        required=True,
        default=lambda self: fields.Date.context_today(self).year,
    )
    budget_id = fields.Many2one(
        "fix.headcount.budget", string="Headcount Budget", readonly=True, copy=False
    )
    over_budget = fields.Boolean(
        string="Beyond Headcount Budget",
        readonly=True,
        copy=False,
        help="Stamped at submission: the requisition takes the scope beyond its approved "
        "headcount budget, so the CFO tier decides it.",
    )
    over_budget_reason = fields.Text(
        string="Over-Budget Justification",
        help="Required to submit a requisition beyond the approved headcount budget.",
    )
    onboarding_template_id = fields.Many2one(
        "fix.onboarding.template",
        string="Onboarding Template",
        help="The task set generated at hire. Empty: the default template.",
    )

    @api.model
    def _default_hiring_manager(self):
        user = self.env.user
        if not self.env.su and user.has_group(HIRING_MANAGER) and not user.has_group(RECRUITER):
            return user
        return False

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "approved_by_id",
            "approved_on",
            "approved_openings",
            "budget_id",
            "over_budget",
        }

    def _approval_group_xmlid(self):
        if self.over_budget:
            return CFO_GROUP
        return super()._approval_group_xmlid()

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

    @api.model_create_multi
    def create(self, vals_list):
        if not _is_recruiter(self.env):
            for vals in vals_list:
                # a hiring manager raises requisitions for themself only
                if vals.get("hiring_manager_id", self.env.uid) != self.env.uid:
                    raise AccessError("A hiring manager raises requisitions in their own name.")
                vals["hiring_manager_id"] = self.env.uid
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open():
            if (
                "hiring_manager_id" in vals
                and not _is_recruiter(self.env)
                and any(
                    r._fix_guard_differs(
                        "hiring_manager_id", vals["hiring_manager_id"], r.hiring_manager_id
                    )
                    for r in self
                )
            ):
                raise AccessError("Only Recruitment names a requisition's hiring manager.")
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

    # ---- the position's seats (M21 fix.org.position.headcount) --------------
    def _fix_claimed_seats(self, position):
        """Seats of `position` already promised to OTHER live requisitions."""
        others = self.sudo().search(
            [
                ("id", "not in", self.ids),
                ("position_id", "=", position.id),
                "|",
                ("state", "in", LIVE_REQ_STATES),
                ("approval_state", "=", "pending"),
            ]
        )
        claimed = 0
        for req in others:
            claimed += req.openings_left if req.state == "open" else req.openings
        return claimed

    def _fix_seat_problems(self):
        """BRU-HCM-10: a position never holds more than its sanctioned headcount,
        so a requisition cannot ask for seats the position does not have."""
        self.ensure_one()
        position = self.position_id.sudo()
        if not position:
            return []
        holders = len(position.employee_ids)
        free = (position.headcount or 0) - holders - self._fix_claimed_seats(position)
        if self.openings > free:
            return [
                "position %s has %d free seat(s) of its sanctioned headcount %d (%d held, the "
                "rest promised to other requisitions); raise the headcount in M21 first "
                "(BRU-HCM-10)" % (position.name, max(free, 0), position.headcount, holders)
            ]
        return []

    # ---- the headcount budget (BRU-TAO-01) -----------------------------------
    def _fix_budget(self):
        """The approved budget covering this requisition: its position's, else
        its department's, for the budget year."""
        self.ensure_one()
        Budget = self.env["fix.headcount.budget"].sudo()
        base = [
            ("company_id", "=", self.company_id.id),
            ("year", "=", self.budget_year),
            ("state", "=", "approved"),
        ]
        if self.position_id:
            budget = Budget.search([*base, ("position_id", "=", self.position_id.id)], limit=1)
            if budget:
                return budget
        if self.department_id:
            return Budget.search(
                [*base, ("department_id", "=", self.department_id.id), ("position_id", "=", False)],
                limit=1,
            )
        return Budget

    def _fix_budget_used(self, budget):
        """Headcount the scope would reach with this requisition: today's holders,
        the openings still to fill on the scope's other live requisitions of the
        year, and this requisition's openings."""
        self.ensure_one()
        budget = budget.sudo()
        if budget.position_id:
            scope = [("position_id", "=", budget.position_id.id)]
            holders = len(budget.position_id.employee_ids)
        else:
            scope = [("department_id", "=", budget.department_id.id)]
            holders = self.env["hr.employee"].sudo().search_count(scope)
        others = self.sudo().search(
            [
                ("id", "not in", self.ids),
                ("company_id", "=", budget.company_id.id),
                ("budget_year", "=", budget.year),
                *scope,
                "|",
                ("state", "in", LIVE_REQ_STATES),
                ("approval_state", "=", "pending"),
            ]
        )
        promised = sum(r.openings_left if r.state == "open" else r.openings for r in others)
        return holders + promised + self.openings

    def _fix_budget_status(self):
        """(budget, used, over) for this requisition now."""
        self.ensure_one()
        budget = self._fix_budget()
        if not budget:
            return budget, 0, False
        used = self._fix_budget_used(budget)
        return budget, used, used > budget.approved_headcount

    def _fix_budget_gate(self):
        """Refuse a requisition beyond its budget unless it carries the
        justification that routes it to the CFO tier. Returns {id: (budget, over)}."""
        required = _int_param(self.env, "cd_talent.require_headcount_budget", 0)
        out = {}
        for rec in self:
            budget, used, over = rec._fix_budget_status()
            if not budget and required:
                raise UserError(
                    "Requisition %s: no approved headcount budget for %s in %d (BRU-TAO-01)."
                    % (
                        rec.name,
                        rec.position_id.name or rec.department_id.name or "its scope",
                        rec.budget_year,
                    )
                )
            if over and not (rec.over_budget_reason or "").strip():
                raise UserError(
                    "Requisition %s takes %s to %d against an approved headcount budget of %d "
                    "for %d (BRU-TAO-01). Give the over-budget justification: the request is "
                    "then decided by the CFO tier."
                    % (
                        rec.name,
                        budget.display_name,
                        used,
                        budget.approved_headcount,
                        rec.budget_year,
                    )
                )
            out[rec.id] = (budget, over)
        return out

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
            problems = rec._fix_seat_problems()
            if problems:
                raise UserError("Requisition %s: %s." % (rec.name, "; ".join(problems)))

    def action_request_approval(self, justification=None):
        _require_recruiter_or_hiring_manager(self.env, self, "submit a requisition")
        self._fix_submit_gate()
        for rec in self:
            budget, over = rec._fix_budget_gate()[rec.id]
            rec._guarded().write({"budget_id": budget.id or False, "over_budget": over})
        return super().action_request_approval(justification=justification)

    def action_approve(self):
        """Routed apply method: the approver opens the requisition."""
        self._approval_assert_routed()
        self._people_assert_not_conflicted()
        self._fix_submit_gate()
        for rec in self:
            # the budget is read again at the decision: another requisition may
            # have used it up since this one was submitted
            _budget, _used, over = rec._fix_budget_status()
            if over and not rec.over_budget:
                raise UserError(
                    "Requisition %s no longer fits its headcount budget. Recall it and submit "
                    "it again with the over-budget justification." % rec.name
                )
            if (
                rec.over_budget
                and not self.env.su
                and not rec._people_decider().has_group(CFO_GROUP)
            ):
                raise UserError(
                    "Requisition %s is beyond its headcount budget: the CFO tier decides it."
                    % rec.name
                )
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

    def _people_conflicted_users(self):
        """M58-F12: the hiring manager is the SUBJECT of a requisition - it asks
        for someone on their team - so they never decide it, even when a
        recruiter created and submitted it (the generic conflict set only
        held the requester, the creator, the preparers and the subject
        EMPLOYEES, which a requisition has none of)."""
        return super()._people_conflicted_users() | self.sudo().mapped("hiring_manager_id")

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
    # M58-F4: nid_number / birth_reg_number / passport_number are declared in
    # fix_candidate_identity.py - they live in the Bangladesh-resident store,
    # and the row keeps only their keyed hashes and pointers.
    nid_hash = fields.Char(
        string="NID Hash", readonly=True, copy=False, index=True, groups="cd_talent.group_talent"
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
            "nid_hash",
        }

    @api.model
    def _fix_ensure_identity_hash_key(self):
        """Create the shared identity hash key once, if M21 has not (install /
        upgrade only; the same idempotent rule as cd_hr_core)."""
        Param = self.env["ir.config_parameter"].sudo()
        if not Param.get_param(IDENTITY_HASH_KEY):
            Param.set_param(IDENTITY_HASH_KEY, secrets.token_hex(32))
        return True

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
        # M58-F4: the hash is what the row keeps; the value itself is in the
        # resident store, so the duplicate check normally reads no value at all
        digest = self.sudo().nid_hash or (
            nid_hash(self.env, self.nid_number) if self.nid_number else False
        )
        if digest:
            keys.append(("nid_hash", "=", digest))
        if not keys:
            return None
        return ["|"] * (len(keys) - 1) + keys

    def _fix_duplicate_message(self, vals, exclude=None):
        """AUT-TAO-03 from the values being written. The stored hash is written
        by the inverse after the row exists (M58-F4), so a new application's NID
        is hashed here from the submitted value - neither path needs the value
        to stay on the row."""
        req = vals.get("requisition_id") or (exclude and exclude.requisition_id.id)
        if not req:
            return None
        keys = []
        if vals.get("email"):
            keys.append(("email", "=ilike", str(vals["email"]).strip()))
        phone = _digits(vals.get("phone"))
        if phone:
            keys.append(("phone", "ilike", phone[-10:]))
        if vals.get("nid_number"):
            keys.append(("nid_hash", "=", nid_hash(self.env, vals["nid_number"])))
        elif exclude is not None and exclude.sudo().nid_hash:
            keys.append(("nid_hash", "=", exclude.sudo().nid_hash))
        if not keys:
            return None
        domain = [
            ("requisition_id", "=", int(req)),
            ("state", "!=", "rejected"),
            *(["|"] * (len(keys) - 1) + keys),
        ]
        if exclude is not None:
            domain.insert(0, ("id", "!=", exclude.id))
        dup = self.sudo().with_context(active_test=False).search(domain, limit=1)
        if not dup:
            return None
        return "%s has already applied to %s (%s): the same email, phone or NID." % (
            vals.get("name") or (exclude and exclude.name) or "This candidate",
            dup.requisition_id.name,
            dup.name,
        )

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
        for vals in vals_list:
            if vals.get("nid_number"):
                vals["nid_number"] = str(vals["nid_number"]).strip()
            message = self._fix_duplicate_message(vals)
            if message:
                raise ValidationError(message)
        recs = super().create(vals_list)
        for rec in recs.filtered("nid_number"):
            rec.sudo()._guarded().write({"nid_hash": nid_hash(rec.env, rec.nid_number)})
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
        if not self._fix_guard_open() and vals.get("nid_number"):
            for rec in self:
                if rec.state == "hired" or rec.erased:
                    raise UserError(
                        "%s is %s: their NID lives on the employee master, not here."
                        % (rec.name, "hired" if rec.state == "hired" else "erased")
                    )
        if vals.get("nid_number"):
            vals = dict(vals, nid_number=str(vals["nid_number"]).strip())
            # M58-F4: the duplicate check from the submitted value, before the
            # hash is written (the value itself is never kept on the row)
            for rec in self:
                message = rec._fix_duplicate_message(vals, exclude=rec)
                if message:
                    raise ValidationError(message)
        result = super().write(vals)
        if "nid_number" in vals:
            for rec in self:
                if rec.nid_number:
                    rec.sudo()._guarded().write({"nid_hash": nid_hash(rec.env, rec.nid_number)})
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
        problems += self._fix_baseline_problems()
        position = (offer.position_id if offer else False) or self.requisition_id.position_id
        if position:
            position = position.sudo()
            if len(position.employee_ids) >= (position.headcount or 0):
                problems.append(
                    "position %s is full (%d sanctioned, BRU-HCM-10)"
                    % (position.name, position.headcount)
                )
        if not self.consent_given:
            problems.append("no recorded consent to processing (BRU-TAO-13)")
        problems += self._fix_age_problems(offer.joining_date if offer else None)
        dup = self._fix_duplicate_hire()
        if dup:
            problems.append("the same person is already hired as %s" % dup.name)
        if self.nid_number:
            # the employee master searches its own (hashed) NID
            twin = (
                self.env["hr.employee"]
                .sudo()
                .with_context(active_test=False)
                .search([("nid_number", "=", self.nid_number.strip())], limit=1)
            )
            if twin:
                problems.append("an employee with this NID already exists (%s)" % twin.name)
        return problems

    # ---- transitions ---------------------------------------------------------
    def _fix_move(self, frm, to, what):
        _require_recruiter_or_hiring_manager(self.env, self.mapped("requisition_id"), what)
        if not _is_recruiter(self.env) and not all(self.mapped("requisition_id")):
            raise AccessError("Only Recruitment works a candidate with no requisition.")
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
            # M58-F20: the age gate ran only at issue and hire, so a minor
            # reached the "offered" stage; the date of birth is verified
            # before the offer (BLA 2006 s.34, BRU-TAO-17)
            problems += rec._fix_age_problems(None)
            if problems:
                raise UserError(
                    "%s cannot move to the offer stage: %s." % (rec.name, "; ".join(problems))
                )
        self._fix_move(("interview",), "offered", "the offer stage")
        return True

    def action_reject(self, reason=None):
        """Close the application with its outcome (BRU-TAO-16)."""
        _require_recruiter_or_hiring_manager(
            self.env, self.mapped("requisition_id"), "reject a candidate"
        )
        if not _is_recruiter(self.env) and not all(self.mapped("requisition_id")):
            raise AccessError("Only Recruitment works a candidate with no requisition.")
        if not (reason or "").strip():
            raise UserError("State the outcome communicated to the candidate.")
        # M58-F3: the owner's figures (2026-11-23) - 180 days for an ordinary
        # applicant, 365 for one who consented to the talent pool.
        plain_days = _int_param(self.env, "cd_talent.candidate_retention_days", 0)
        pool_days = _int_param(self.env, "cd_talent.talent_pool_retention_days", 0)
        for rec in self:
            if rec.state in ("hired", "rejected"):
                raise UserError("%s is already %s." % (rec.name, rec.state))
            days = pool_days if (pool_days and rec.talent_pool_consent) else plain_days
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
            # M58-F4: each identifier the store serves back intact is copied to
            # the employee master and released here; none stays in clear.
            rec._fix_release_identity(emp)
            contract = rec._fix_create_contract(emp, accepted)
            rec._guarded().write(
                {"state": "hired", "employee_id": emp.id, "hired_on": fields.Datetime.now()}
            )
            rec._fix_carry_baseline(emp)
            plan = rec._fix_open_onboarding(emp, contract, accepted)
            plan._fix_generate_appointment_letter()
            plan._fix_generate_tasks()
            rec.requisition_id.sudo()._fix_refresh_fill()
        return True

    # ---- BRU-TAO-12: the assessment becomes the M22 baseline -----------------
    def _fix_passed_assessments(self):
        self.ensure_one()
        return (
            self.env["fix.talent.assessment"]
            .sudo()
            .search([("candidate_id", "=", self.id), ("passed", "=", True)])
        )

    def _fix_baseline_problems(self):
        unmapped = self._fix_passed_assessments().filtered(lambda a: not a.competency_id)
        if unmapped:
            return [
                "passed assessment %s names no M22 competency, so it cannot become the "
                "competency baseline (BRU-TAO-12)" % ", ".join(unmapped.mapped("name"))
            ]
        return []

    def _fix_carry_baseline(self, employee):
        """The passed practical assessments become the new employee's first M22
        assessments. Created with sudo, M22's trusted path: the assessor and
        score are the M58 record's, and the assessee never records their own."""
        self.ensure_one()
        M22 = self.env["fix.competency.assessment"].sudo()
        for asmt in self._fix_passed_assessments().filtered(lambda a: not a.baseline_id):
            baseline = M22.create(
                {
                    "employee_id": employee.id,
                    "competency_id": asmt.competency_id.id,
                    "company_id": asmt.company_id.id,
                    "assessed_on": asmt.assessed_on,
                    "assessor_id": asmt.assessor_id.id or False,
                    "level": asmt.level or "l2",
                    "score": asmt.score,
                    "notes": "Competency baseline from the M58 practical assessment %s "
                    "(BRU-TAO-12)." % asmt.name,
                }
            )
            asmt._guarded().write(
                {"baseline_id": baseline.id, "baseline_on": fields.Datetime.now()}
            )

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
            # M58-F4: the store-held identifiers leave first (a store that is
            # down leaves one for the next run; the record is still anonymised)
            rec._fix_identity_erase()
            rec._guarded().write(
                {
                    "name": "Erased candidate %d" % rec.id,
                    "email": False,
                    "phone": False,
                    "nid_hash": False,
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
    # M24 / BLA 2006 s.5: the appointment letter is GENERATED at hire from the
    # accepted offer and the draft contract, and the employee acknowledges it:
    # in person (their own login), or by signing it, when a verifier other
    # than the uploader attests the employee-signed counterpart.
    appointment_letter_id = fields.Many2one(
        "fix.hr.document", string="Generated Appointment Letter", readonly=True, copy=False
    )
    signed_contract_file = fields.Binary(
        string="Employee-Signed Appointment Letter", attachment=True, copy=False
    )
    signed_contract_filename = fields.Char(copy=False)
    signed_contract_uploaded_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    appointment_ack_method = fields.Selection(
        [
            ("employee", "Acknowledged by the employee in the system"),
            ("signed_counterpart", "Employee-signed counterpart, attested"),
        ],
        string="Appointment Letter Acknowledged By",
        readonly=True,
        copy=False,
    )
    appointment_ack_attested_by_id = fields.Many2one(
        "res.users", string="Signature Attested By", readonly=True, copy=False
    )
    appointment_ack_on = fields.Datetime(readonly=True, copy=False)
    contract_signed = fields.Boolean(
        string="Appointment Letter Acknowledged",
        compute="_compute_evidence",
        help="BLA 2006 s.5: the generated appointment letter exists and the employee "
        "acknowledged it; the draft contract exists.",
    )
    task_ids = fields.One2many("fix.onboarding.task", "plan_id", string="Onboarding Tasks")
    open_mandatory_tasks = fields.Integer(
        compute="_compute_task_counts", string="Mandatory Tasks Open"
    )
    task_count = fields.Integer(compute="_compute_task_counts", string="Tasks")
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
            "appointment_letter_id",
            "signed_contract_uploaded_by_id",
            "appointment_ack_method",
            "appointment_ack_attested_by_id",
            "appointment_ack_on",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(r.state in ("completed", "cancelled") or r.appointment_ack_method for r in self):
            locked |= {"signed_contract_file", "signed_contract_filename"}
        if any(r.state in ("completed", "cancelled") for r in self):
            locked |= {"joined_date"}
        return locked

    @api.depends("task_ids.state", "task_ids.mandatory")
    def _compute_task_counts(self):
        for rec in self:
            tasks = rec.sudo().task_ids
            rec.task_count = len(tasks)
            rec.open_mandatory_tasks = len(
                tasks.filtered(lambda t: t.mandatory and t.state != "done")
            )

    def write(self, vals):
        if not self._fix_guard_open() and {"signed_contract_file", "joined_date"} & set(vals):
            for rec in self:
                if rec.id and rec.state in ("completed", "cancelled"):
                    raise UserError("%s is %s; its evidence is frozen." % (rec.name, rec.state))
                if (
                    rec.id
                    and "signed_contract_file" in vals
                    and rec.appointment_ack_method
                    and rec._fix_guard_differs(
                        "signed_contract_file",
                        vals["signed_contract_file"],
                        rec.signed_contract_file,
                    )
                ):
                    raise UserError(
                        "The appointment letter of %s is acknowledged; its signed copy is a "
                        "record." % rec.name
                    )
        result = super().write(vals)
        if "signed_contract_file" in vals and not self.env.su:
            # who uploaded the counterpart never attests it
            self._guarded().write(
                {
                    "signed_contract_uploaded_by_id": self.env.uid
                    if vals["signed_contract_file"]
                    else False
                }
            )
        return result

    # ---- the appointment letter (M24, BLA 2006 s.5, BRU-TAO-08) --------------
    def _fix_appointment_text(self):
        self.ensure_one()
        emp = self.employee_id.sudo()
        offer = self.offer_id.sudo()
        contract = self.contract_id.sudo()
        company = self.company_id.sudo()
        types = dict(offer._fields["contract_type"].selection)
        cur = offer.currency_id.name or "BDT"
        return (
            "APPOINTMENT LETTER (Bangladesh Labour Act 2006 s.5; Labour Rules 2015 r.19, "
            "Form 6)\n"
            "Employer: %s\n"
            "Appointee: %s\n"
            "Position: %s\n"
            "Department: %s\n"
            "Date of joining: %s\n"
            "Nature of employment: %s\n"
            "Basic monthly wage: %s %s\n"
            "Gross monthly wage: %s %s\n"
            "Contract reference: %s\n"
            "Offer reference: %s (approved by %s on %s)\n"
            "Generated by the system from the accepted offer and the draft contract; "
            "valid once acknowledged by the appointee.\n"
            % (
                company.name,
                emp.name,
                (offer.position_id or self.position_id).name or "",
                self.department_id.name or "",
                offer.joining_date or self.joined_date,
                types.get(offer.contract_type, offer.contract_type or ""),
                cur,
                f"{contract.basic_monthly or offer.basic_salary or 0.0:,.2f}",
                cur,
                f"{offer.approved_gross or offer.gross_salary or 0.0:,.2f}",
                contract.name or "",
                offer.name or "",
                offer.approved_by_id.name or "",
                offer.approved_on or "",
            )
        )

    def _fix_generate_appointment_letter(self):
        """Generated once, at hire, as the employee's M21 statutory document
        (an unsigned, system-written fix.hr.document)."""
        Doc = self.env["fix.hr.document"].sudo()
        for rec in self.filtered(lambda r: r.employee_id and not r.appointment_letter_id):
            emp = rec.employee_id.sudo()
            doc = Doc._guarded().create(
                {
                    "employee_id": emp.id,
                    "company_id": rec.company_id.id,
                    "doc_type": "appointment",
                    "reference": "APPT/%s" % (rec.offer_id.name or rec.id),
                    "issued_on": fields.Date.context_today(rec),
                    "generated": True,
                    "verified": False,
                    "file_name": "Appointment_Letter_%s.txt" % (rec.offer_id.name or rec.id),
                    "file_data": base64.b64encode(rec._fix_appointment_text().encode()),
                }
            )
            rec._guarded().write({"appointment_letter_id": doc.id})
        return True

    def _fix_require_letter(self):
        for rec in self:
            if rec.state not in ("draft", "in_progress"):
                raise UserError("%s is %s." % (rec.name, rec.state))
            if not rec.appointment_letter_id:
                raise UserError("%s has no generated appointment letter." % rec.name)
            if rec.appointment_ack_method:
                raise UserError("The appointment letter of %s is already acknowledged." % rec.name)

    def action_acknowledge_appointment(self):
        """The employee acknowledges their own appointment letter."""
        self._fix_require_letter()
        for rec in self:
            if not self.env.su and rec.employee_id.sudo().user_id != self.env.user:
                raise AccessError(
                    "Only %s acknowledges their appointment letter." % rec.employee_id.sudo().name
                )
            now = fields.Datetime.now()
            rec.appointment_letter_id.sudo()._guarded().write(
                {"acknowledged": True, "acknowledged_on": now}
            )
            # the identity was checked above; the employee holds no plan write
            rec.sudo()._guarded().write(
                {"appointment_ack_method": "employee", "appointment_ack_on": now}
            )
        return True

    def action_attest_signed_appointment(self):
        """A Background Verifier, not the person who uploaded it, attests the
        employee-signed counterpart: the signature is the employee's
        acknowledgement. The signed scan becomes the verified document."""
        if not (self.env.su or self.env.user.has_group("cd_talent.group_background_verifier")):
            raise AccessError("A Background Verifier attests a signed appointment letter.")
        self._fix_require_letter()
        for rec in self:
            if not rec.signed_contract_file:
                raise UserError(
                    "Attach the appointment letter signed by %s first."
                    % rec.employee_id.sudo().name
                )
            if not self.env.su and self.env.user in (
                rec.signed_contract_uploaded_by_id | rec.employee_id.sudo().user_id
            ):
                raise UserError(
                    "You uploaded (or are the subject of) this signed copy; another verifier "
                    "attests it."
                )
            now = fields.Datetime.now()
            doc = rec.appointment_letter_id.sudo()
            # a new file resets the generated flag: the signed scan is the record
            doc._guarded().write(
                {
                    "file_data": rec.signed_contract_file,
                    "file_name": rec.signed_contract_filename or doc.file_name,
                    "generated": False,
                    "verified": True,
                    "verified_by_id": self.env.uid,
                    "verified_on": now,
                    "acknowledged": True,
                    "acknowledged_on": now,
                }
            )
            rec.sudo()._guarded().write(
                {
                    "appointment_ack_method": "signed_counterpart",
                    "appointment_ack_attested_by_id": self.env.uid,
                    "appointment_ack_on": now,
                }
            )
        return True

    # ---- onboarding tasks (FR-TAO-027, T-07) ----------------------------------
    def _fix_template(self):
        self.ensure_one()
        Template = self.env["fix.onboarding.template"].sudo()
        tpl = self.requisition_id.sudo().onboarding_template_id
        if tpl and tpl.active:
            return tpl
        return Template.search(
            [("is_default", "=", True), ("company_id", "in", (self.company_id.id, False))],
            order="company_id desc, id",  # a company's own default first
            limit=1,
        )

    def _fix_generate_tasks(self):
        """The task set of the template, with owners and due dates, created
        once per template line (idempotent)."""
        Task = self.env["fix.onboarding.task"].sudo()
        for rec in self:
            tpl = rec._fix_template()
            if not tpl:
                continue
            req = rec.requisition_id.sudo()
            done = set(rec.sudo().task_ids.mapped("template_line_id").ids)
            fallback = req.hiring_manager_id or self.env.user
            for line in tpl.line_ids.filtered(
                lambda ln, r=req: r.is_field_role or not ln.field_role_only
            ):
                if line.id in done:
                    continue
                Task._guarded().create(
                    {
                        "plan_id": rec.id,
                        "template_line_id": line.id,
                        "name": line.name,
                        "function": line.function,
                        "owner_id": (line.owner_user_id or fallback).id,
                        "due_date": rec.joined_date + timedelta(days=line.due_offset_days),
                        "mandatory": line.mandatory,
                        "evidence_required": line.evidence_required,
                    }
                )
        return True

    _EVIDENCE = (
        "nid_verified",
        "contract_signed",
        "bank_details_captured",
        "keycloak_provisioned",
        "safety_kit_issued",
    )

    @api.depends(
        "appointment_ack_method",
        "appointment_letter_id",
        "contract_id",
        "employee_id",
        "candidate_id",
    )
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
            letter = rec.appointment_letter_id.sudo()
            rec.contract_signed = bool(
                rec.contract_id and letter and letter.acknowledged and rec.appointment_ack_method
            )
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
        if not self.appointment_letter_id:
            problems.append("no generated appointment letter (BLA s.5)")
        elif not self.contract_signed:
            problems.append(
                "the appointment letter is not acknowledged by the employee (BLA s.5): their "
                "own acknowledgement, or their signed copy attested by a verifier"
            )
        open_tasks = self.sudo().task_ids.filtered(lambda t: t.mandatory and t.state != "done")
        if open_tasks:
            problems.append(
                "%d mandatory onboarding task(s) not done: %s"
                % (len(open_tasks), ", ".join(open_tasks.mapped("name")))
            )
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
