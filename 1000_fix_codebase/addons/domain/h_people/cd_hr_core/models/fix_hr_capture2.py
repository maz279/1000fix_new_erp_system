# cd_hr_core - the M21 records the second capture audit found missing
# (M21 capture audit pass 2, 2026-11-19).
#
# - Employment Contracts / Lifecycle: a probation was confirmed or extended by
#   a bare button, with no review evidence (FR-HCM-016/029, AUT-HCM-03,
#   KPI-218). fix.hr.probation.review is the line manager's assessment; HR
#   confirms or extends only on a submitted review that recommends it, and
#   never on a review they wrote themselves.
# - Org Structure: an employee could hold one position and one solid-line
#   manager only. The spec's dual-role record (BRU-HCM-10 H, T-06), acting
#   charge and dotted-line reporting (FR-HCM-024) had no record at all.
#   fix.hr.additional.assignment is that record; an approved dual role takes
#   a sanctioned seat like any holder.
# - Exit Process: the clearance had no knowledge handover (FR-HCM-036). The
#   leaver's open jobs, customers, files and shared accounts went nowhere.
#   fix.hr.exit.handover names the successor, and HR's clearance tick waits
#   for the successor (or the line manager) to accept it.
# - ESS / MSS: an employee could request a change to bank, MFS, NID and e-TIN
#   only. Address, personal contact, emergency contact and family details
#   (FR-HCM-040/042) now go through the same maker-checker request.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_hr_capture import RATING
from .fix_hr_controls_common import OFFICER
from .fix_hr_exit_controls import TICKS

RECOMMENDATIONS = [
    ("confirm", "Confirm in Service"),
    ("extend", "Extend Probation (skilled worker, once, 3 months)"),
    ("not_confirm", "Do Not Confirm"),
]


def _today(env):
    return fields.Date.context_today(env["res.users"])


class FixHrProbationReview(models.Model):
    """The line manager's end-of-probation assessment (FR-HCM-016/029).

    The review is evidence: once submitted its answers are fixed. HR decides
    the probation from it (fix.employment.contract), and the person deciding
    is never the person who reviewed."""

    _name = "fix.hr.probation.review"
    _description = "Probation Review"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "review_date desc, id desc"

    _ANSWER_FIELDS = (
        "employee_id",
        "reviewer_id",
        "review_date",
        "rating_attendance",
        "rating_quality",
        "rating_skill",
        "rating_conduct",
        "rating_customer",
        "strengths",
        "concerns",
        "recommendation",
        "evidence_file",
    )
    _REQUIRED_RATINGS = ("rating_attendance", "rating_quality", "rating_skill", "rating_conduct")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "submitted_on", "submitted_by_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= set(self._ANSWER_FIELDS)
        return locked

    name = fields.Char(compute="_compute_name", store=True, string="Reference")
    company_id = fields.Many2one(related="contract_id.company_id", store=True, index=True)
    # The reviewer picks the employee; the server resolves their active
    # probation contract (a line manager cannot read contracts: salary).
    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        required=True,
        index=True,
        ondelete="restrict",
        domain=[("fix_on_probation", "=", True)],
    )
    contract_id = fields.Many2one(
        "fix.employment.contract",
        string="Probation Contract",
        required=True,
        readonly=True,
        index=True,
        ondelete="restrict",
    )
    probation_class = fields.Selection(related="contract_id.probation_class")
    probation_end = fields.Date(related="contract_id.probation_end", string="Probation Ends")
    reviewer_id = fields.Many2one(
        "res.users",
        string="Reviewer (line manager)",
        required=True,
        default=lambda self: self.env.user,
    )
    review_date = fields.Date(
        string="Review Date", required=True, default=fields.Date.context_today
    )
    rating_attendance = fields.Selection(RATING, string="Attendance & Punctuality")
    rating_quality = fields.Selection(RATING, string="Quality of Work")
    rating_skill = fields.Selection(RATING, string="Technical Skill")
    rating_conduct = fields.Selection(RATING, string="Conduct & Discipline")
    rating_customer = fields.Selection(RATING, string="Customer Handling")
    strengths = fields.Text(string="Strengths")
    concerns = fields.Text(string="Concerns / Development Needs")
    recommendation = fields.Selection(RECOMMENDATIONS, string="Recommendation", required=True)
    evidence_file = fields.Binary(string="Signed Review Form / Evidence", attachment=True)
    evidence_filename = fields.Char(string="Evidence Filename")
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted")],
        default="draft",
        required=True,
        tracking=True,
    )
    submitted_on = fields.Datetime(string="Submitted On", readonly=True)
    submitted_by_id = fields.Many2one("res.users", string="Submitted By", readonly=True)

    @api.depends("contract_id", "review_date")
    def _compute_name(self):
        for rec in self:
            rec.name = "PRB/%s/%s" % (rec.contract_id.name or "?", rec.review_date or "?")

    @api.model
    def _fix_probation_contract(self, employee_id):
        """The employee's active probation contract (read as superuser: the
        reviewing line manager holds no right on contracts)."""
        contract = (
            self.env["fix.employment.contract"]
            .sudo()
            .search(
                [
                    ("employee_id", "=", employee_id),
                    ("contract_type", "=", "probation"),
                    ("state", "=", "active"),
                ],
                order="joining_date desc, id desc",
                limit=1,
            )
        )
        if not contract:
            emp = self.env["hr.employee"].sudo().browse(employee_id)
            raise UserError("%s has no active probation contract to review." % emp.name)
        return contract

    @api.constrains("contract_id", "employee_id", "reviewer_id", "review_date")
    def _check_review(self):
        today = _today(self.env)
        for rec in self:
            contract = rec.contract_id.sudo()
            if contract.employee_id != rec.employee_id:
                raise ValidationError("The review's contract belongs to another employee.")
            if contract.contract_type != "probation" or contract.state != "active":
                raise ValidationError(
                    "%s is not an active probation contract: there is no probation to review."
                    % contract.name
                )
            subject = contract.employee_id.sudo().user_id
            if subject and rec.reviewer_id == subject:
                raise ValidationError("An employee cannot review their own probation.")
            if rec.review_date and rec.review_date > today:
                raise ValidationError("A review cannot be dated in the future.")

    @api.model
    def _fix_check_author_of(self, employees):
        """HR or the employee's line manager writes a review; never its subject."""
        if self.env.su:
            return
        user = self.env.user
        for emp in employees.sudo():
            if emp.user_id and emp.user_id == user:
                raise UserError("An employee cannot review their own probation.")
            if not (user.has_group(OFFICER) or emp.parent_id.user_id == user):
                raise UserError(
                    "A probation review is written by %s's line manager or by HR." % emp.name
                )

    def _fix_check_author(self):
        self._fix_check_author_of(self.mapped("employee_id"))

    @api.model_create_multi
    def create(self, vals_list):
        Employee = self.env["hr.employee"]
        for vals in vals_list:
            # who writes it is checked before anything is stored
            self._fix_check_author_of(Employee.browse(vals.get("employee_id") or []))
            # the contract is the server's to resolve, never the client's
            if vals.get("employee_id"):
                vals["contract_id"] = self._fix_probation_contract(vals["employee_id"]).id
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open():
            self._fix_check_author()
            if vals.get("employee_id"):
                self._fix_check_author_of(self.env["hr.employee"].browse(vals["employee_id"]))
            if "contract_id" in vals and any(
                rec._fix_guard_differs("contract_id", vals["contract_id"], rec.contract_id)
                for rec in self
            ):
                raise UserError("The probation contract follows the employee reviewed.")
            if vals.get("employee_id"):
                vals = dict(vals, contract_id=self._fix_probation_contract(vals["employee_id"]).id)
            for rec in self.filtered(lambda r: r.state != "draft"):
                changed = {
                    name
                    for name in set(self._ANSWER_FIELDS) & set(vals)
                    if rec._fix_guard_differs(name, vals[name], rec[name])
                }
                if changed:
                    raise UserError(
                        "Probation review %s is submitted and cannot be edited." % rec.name
                    )
        return super().write(vals)

    def unlink(self):
        if not self.env.su and any(r.state != "draft" for r in self):
            raise UserError("A submitted probation review is evidence and is kept.")
        return super().unlink()

    def action_submit(self):
        self._fix_check_author()
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is already submitted." % rec.name)
            missing = [rec._fields[n].string for n in self._REQUIRED_RATINGS if not rec[n]]
            if missing:
                raise UserError("Rate %s before submitting." % ", ".join(missing))
            if rec.recommendation == "extend":
                contract = rec.contract_id.sudo()
                if contract.probation_class != "skilled":
                    raise UserError(
                        "Only a skilled worker's probation may be extended (BLA s.4(8))."
                    )
                if contract.probation_extended:
                    raise UserError("%s was already extended once." % contract.name)
            if rec.recommendation in ("extend", "not_confirm") and not (rec.concerns or "").strip():
                raise UserError("State the concerns behind the recommendation.")
            rec._guarded().write(
                {
                    "state": "submitted",
                    "submitted_on": fields.Datetime.now(),
                    "submitted_by_id": self.env.uid,
                }
            )
            rec.message_post(
                body="Probation review submitted: %s."
                % dict(RECOMMENDATIONS).get(rec.recommendation)
            )
        return True


class HrEmployeeOnProbation(models.Model):
    _inherit = "hr.employee"

    fix_on_probation = fields.Boolean(
        string="On Probation",
        compute="_compute_fix_on_probation",
        search="_search_fix_on_probation",
        help="Holds an active probation contract.",
    )

    def _fix_probation_employee_ids(self):
        contracts = (
            self.env["fix.employment.contract"]
            .sudo()
            .search([("contract_type", "=", "probation"), ("state", "=", "active")])
        )
        return set(contracts.mapped("employee_id").ids)

    def _compute_fix_on_probation(self):
        on = self._fix_probation_employee_ids()
        for emp in self:
            emp.fix_on_probation = emp.id in on

    def _search_fix_on_probation(self, operator, value):
        if operator not in ("=", "!=") or not isinstance(value, bool):
            raise UserError("Search 'On Probation' with = True or = False.")
        positive = (operator == "=") == value
        return [("id", "in" if positive else "not in", list(self._fix_probation_employee_ids()))]


class FixEmploymentContractProbationReview(models.Model):
    """HR confirms or extends a probation on a submitted review only."""

    _inherit = "fix.employment.contract"

    probation_review_ids = fields.One2many(
        "fix.hr.probation.review", "contract_id", string="Probation Reviews"
    )
    probation_review_id = fields.Many2one(
        "fix.hr.probation.review",
        string="Decided on Review",
        readonly=True,
        copy=False,
        help="The submitted review HR confirmed or extended this probation on.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"probation_review_id"}

    def _fix_decision_review(self, recommendation, what):
        """The latest submitted review of this contract, which must recommend
        `recommendation` and not have been written by the deciding user."""
        self.ensure_one()
        review = (
            self.env["fix.hr.probation.review"]
            .sudo()
            .search(
                [("contract_id", "=", self.id), ("state", "=", "submitted")],
                order="review_date desc, id desc",
                limit=1,
            )
        )
        if not review:
            raise UserError(
                "%s: %s needs a submitted probation review from the line manager "
                "(FR-HCM-029)." % (self.name, what)
            )
        if review.recommendation != recommendation:
            raise UserError(
                "%s: the latest probation review (%s) recommends '%s', not this decision."
                % (self.name, review.name, dict(RECOMMENDATIONS).get(review.recommendation))
            )
        if not self.env.su and self.env.user in (review.reviewer_id | review.submitted_by_id):
            raise UserError(
                "You reviewed %s's probation: another HR officer decides it."
                % self.employee_id.sudo().name
            )
        return review

    def action_confirm_probation(self):
        self._fix_check_probation_decider("Confirming a probation")
        reviews = {rec.id: rec._fix_decision_review("confirm", "Confirming") for rec in self}
        result = super().action_confirm_probation()
        for rec in self:
            rec._guarded().write({"probation_review_id": reviews[rec.id].id})
        return result

    def action_extend_probation(self):
        self._fix_check_probation_decider("Extending a probation")
        # the statutory refusals first, as before; then the review
        for rec in self:
            if rec.probation_class != "skilled":
                raise UserError("Only a skilled worker's probation may be extended (BLA s.4(8)).")
            if rec.probation_extended:
                raise UserError("%s was already extended once." % rec.name)
        reviews = {rec.id: rec._fix_decision_review("extend", "Extending") for rec in self}
        result = super().action_extend_probation()
        for rec in self:
            rec._guarded().write({"probation_review_id": reviews[rec.id].id})
        return result


ASSIGNMENT_TYPES = [
    ("dual_role", "Dual Role (holds a second position)"),
    ("acting", "Acting Charge (covers a position)"),
    ("dotted_line", "Dotted-Line Reporting"),
]


class FixHrAdditionalAssignment(models.Model):
    """A second position, an acting charge or a dotted-line manager, beside
    the employee's one primary position and solid-line manager (FR-HCM-024,
    BRU-HCM-10, T-06). Approved by an HR officer who did not raise it."""

    _name = "fix.hr.additional.assignment"
    _description = "Additional Assignment (Dual Role / Acting / Dotted Line)"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "date_from desc, id desc"

    _TERMS = ("employee_id", "assignment_type", "position_id", "manager_id", "date_from", "reason")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "approved_by_id",
            "approved_on",
            "ended_on",
            "ended_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= set(self._TERMS) | {"date_to"}
        return locked

    name = fields.Char(compute="_compute_name", store=True, string="Reference")
    company_id = fields.Many2one(related="employee_id.company_id", store=True, index=True)
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, index=True, ondelete="restrict"
    )
    primary_position_id = fields.Many2one(
        related="employee_id.position_id", string="Primary Position"
    )
    assignment_type = fields.Selection(ASSIGNMENT_TYPES, string="Assignment Type", required=True)
    position_id = fields.Many2one(
        "fix.org.position", string="Additional / Acting Position", index=True, ondelete="restrict"
    )
    manager_id = fields.Many2one(
        "hr.employee", string="Dotted-Line Manager", index=True, ondelete="restrict"
    )
    date_from = fields.Date(
        string="Effective From", required=True, default=fields.Date.context_today
    )
    date_to = fields.Date(string="Effective To")
    reason = fields.Text(string="Reason", required=True)
    order_file = fields.Binary(string="Office Order", attachment=True)
    order_filename = fields.Char(string="Office Order Filename")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("approved", "Approved"),
            ("ended", "Ended"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True)
    approved_on = fields.Datetime(string="Approved On", readonly=True)
    ended_on = fields.Date(string="Ended On", readonly=True)
    ended_by_id = fields.Many2one("res.users", string="Ended By", readonly=True)

    @api.depends("employee_id", "assignment_type", "date_from")
    def _compute_name(self):
        for rec in self:
            rec.name = "ADA/%s/%s/%s" % (
                rec.employee_id.employee_code or rec.employee_id.id or "?",
                rec.assignment_type or "?",
                rec.date_from or "?",
            )

    def _fix_live_on(self, day):
        return self.filtered(
            lambda a: a.state == "approved"
            and a.date_from <= day
            and (not a.date_to or a.date_to >= day)
        )

    @api.constrains(
        "employee_id", "assignment_type", "position_id", "manager_id", "date_from", "date_to"
    )
    def _check_terms(self):
        for rec in self:
            emp = rec.employee_id.sudo()
            if rec.date_to and rec.date_to < rec.date_from:
                raise ValidationError("An assignment cannot end before it starts.")
            if rec.assignment_type in ("dual_role", "acting"):
                if not rec.position_id:
                    raise ValidationError("A dual role or acting charge names the position.")
                if rec.position_id == emp.position_id:
                    raise ValidationError(
                        "%s already holds %s as their primary position."
                        % (emp.name, rec.position_id.name)
                    )
                if rec.position_id.company_id and rec.position_id.company_id != emp.company_id:
                    raise ValidationError("The position belongs to another company.")
            if rec.assignment_type == "acting" and not rec.date_to:
                raise ValidationError("An acting charge is temporary: give its end date.")
            if rec.assignment_type == "dotted_line":
                if not rec.manager_id:
                    raise ValidationError("A dotted-line assignment names the manager.")
                if rec.manager_id == emp:
                    raise ValidationError("An employee cannot report to themselves.")
                if rec.manager_id == emp.parent_id:
                    raise ValidationError(
                        "%s is already the solid-line manager." % rec.manager_id.name
                    )

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su and not self.env.user.has_group(OFFICER):
            raise UserError("Only HR records an additional assignment (BRU-HCM-14).")
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.state != "draft"):
                changed = {
                    name
                    for name in (set(self._TERMS) | {"date_to"}) & set(vals)
                    if rec._fix_guard_differs(name, vals[name], rec[name])
                }
                if changed:
                    raise UserError(
                        "%s is %s: end it and raise a new assignment instead."
                        % (rec.name, dict(rec._fields["state"].selection).get(rec.state))
                    )
        return super().write(vals)

    def _fix_overlaps(self):
        self.ensure_one()
        domain = [
            ("id", "!=", self.id),
            ("employee_id", "=", self.employee_id.id),
            ("assignment_type", "=", self.assignment_type),
            ("state", "=", "approved"),
            ("date_from", "<=", self.date_to or "9999-12-31"),
            "|",
            ("date_to", "=", False),
            ("date_to", ">=", self.date_from),
        ]
        if self.assignment_type == "dotted_line":
            domain.append(("manager_id", "=", self.manager_id.id))
        else:
            domain.append(("position_id", "=", self.position_id.id))
        return self.sudo().search(domain, limit=1)

    def action_approve(self):
        if not (self.env.su or self.env.user.has_group(OFFICER)):
            raise UserError("Only HR approves an additional assignment.")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft assignment is approved.")
            if not self.env.su and self.env.user in (
                rec.sudo().create_uid | rec.employee_id.sudo().user_id
            ):
                raise UserError(
                    "You raised %s or are its subject: another HR officer approves it." % rec.name
                )
            twin = rec._fix_overlaps()
            if twin:
                raise UserError("%s already covers this period (%s)." % (twin.name, rec.name))
            if rec.assignment_type == "dual_role":
                position = rec.position_id.sudo()
                if position.frozen:
                    raise UserError("Position %s is frozen: it takes no holder." % position.name)
                held = len(position.employee_ids) + len(position._fix_dual_role_holders())
                if held >= (position.headcount or 0):
                    raise UserError(
                        "Position %s is full (%d of %d sanctioned seats): a dual role needs a "
                        "free sanctioned seat (BRU-HCM-10)."
                        % (position.name, held, position.headcount)
                    )
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.uid,
                    "approved_on": fields.Datetime.now(),
                }
            )
            rec.message_post(body="Approved.")
        return True

    def action_end(self):
        if not (self.env.su or self.env.user.has_group(OFFICER)):
            raise UserError("Only HR ends an additional assignment.")
        today = _today(self.env)
        for rec in self:
            if rec.state != "approved":
                raise UserError("Only an approved assignment is ended.")
            vals = {"state": "ended", "ended_on": today, "ended_by_id": self.env.uid}
            if not rec.date_to or rec.date_to > today:
                vals["date_to"] = max(today, rec.date_from)
            rec._guarded().write(vals)
        return True

    def action_cancel(self):
        if not (self.env.su or self.env.user.has_group(OFFICER)):
            raise UserError("Only HR cancels an additional assignment.")
        for rec in self:
            if rec.state != "draft":
                raise UserError("An approved assignment is ended, not cancelled.")
            rec._guarded().write({"state": "cancelled"})
        return True


class FixOrgPositionDualRole(models.Model):
    """An approved, current dual role takes a sanctioned seat (BRU-HCM-10)."""

    _inherit = "fix.org.position"

    additional_assignment_ids = fields.One2many(
        "fix.hr.additional.assignment", "position_id", string="Dual Roles & Acting Charges"
    )

    def _fix_dual_role_holders(self):
        """Employees holding this seat today through an approved dual role
        (not counting anyone whose primary position it already is)."""
        self.ensure_one()
        live = (
            self.sudo()
            .additional_assignment_ids.filtered(lambda a: a.assignment_type == "dual_role")
            ._fix_live_on(_today(self.env))
        )
        return live.mapped("employee_id") - self.sudo().employee_ids

    def _compute_filled(self):
        super()._compute_filled()
        for rec in self:
            if not rec.id:
                continue
            filled = rec.filled_count + len(rec._fix_dual_role_holders())
            rec.filled_count = filled
            rec.vacant_count = max((rec.headcount or 0) - filled, 0)

    @api.constrains("headcount")
    def _check_headcount_covers_holders(self):
        super()._check_headcount_covers_holders()
        for rec in self:
            held = len(rec.sudo().employee_ids) + len(rec._fix_dual_role_holders())
            if held > rec.headcount:
                raise ValidationError(
                    "%s has %d holders including dual roles: its headcount cannot drop to %d."
                    % (rec.name, held, rec.headcount)
                )


class HrEmployeeSeatWithDualRoles(models.Model):
    _inherit = "hr.employee"

    additional_assignment_ids = fields.One2many(
        "fix.hr.additional.assignment", "employee_id", string="Additional Assignments"
    )

    @api.constrains("position_id")
    def _check_position_seat(self):
        super()._check_position_seat()
        for position in self.mapped("position_id").sudo():
            held = len(position.employee_ids) + len(position._fix_dual_role_holders())
            if held > position.headcount:
                raise ValidationError(
                    "Position %s is full (%d sanctioned) counting its approved dual roles "
                    "(BRU-HCM-10)." % (position.name, position.headcount)
                )


class FixHrTransferSeatWithDualRoles(models.Model):
    _inherit = "fix.hr.transfer"

    def _fix_check_seat(self):
        super()._fix_check_seat()
        position = self.to_position_id.sudo()
        holders = (position.employee_ids | position._fix_dual_role_holders()) - self.employee_id
        if len(holders) >= (position.headcount or 0):
            raise UserError(
                "Position %s is full (%d of %d sanctioned seats, counting approved dual "
                "roles): no dual occupancy (BRU-HCM-10)."
                % (position.name, len(holders), position.headcount)
            )


class FixHrExitHandover(models.Model):
    """The leaver's knowledge handover (FR-HCM-036): open work, customers,
    files and shared accounts, handed to a named successor who accepts it."""

    _name = "fix.hr.exit.handover"
    _description = "Exit Knowledge Handover"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "handover_date desc, id desc"

    _CONTENT = (
        "exit_id",
        "successor_id",
        "handover_date",
        "open_work",
        "accounts_contacts",
        "documents_files",
        "systems_access",
        "van_stock_ref",
        "pending_notes",
        "handover_file",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "handed_on",
            "handed_by_id",
            "accepted_on",
            "accepted_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= set(self._CONTENT)
        return locked

    name = fields.Char(compute="_compute_name", store=True, string="Reference")
    company_id = fields.Many2one(related="exit_id.company_id", store=True, index=True)
    exit_id = fields.Many2one(
        "fix.hr.exit", string="Exit", required=True, index=True, ondelete="cascade"
    )
    employee_id = fields.Many2one(
        related="exit_id.employee_id", store=True, string="Leaver", index=True
    )
    exit_type = fields.Selection(related="exit_id.exit_type", string="Exit Type")
    last_working_day = fields.Date(related="exit_id.last_working_day", string="Last Working Day")
    successor_id = fields.Many2one(
        "hr.employee", string="Handed Over To", required=True, index=True, ondelete="restrict"
    )
    handover_date = fields.Date(
        string="Handover Date", required=True, default=fields.Date.context_today
    )
    open_work = fields.Text(string="Open Jobs, Tickets & Customer Commitments", required=True)
    accounts_contacts = fields.Text(string="Customers, Suppliers & Contacts Handed Over")
    documents_files = fields.Text(string="Documents, Files & Records (where they are)")
    systems_access = fields.Text(string="Shared Accounts & Passwords to Reset")
    van_stock_ref = fields.Char(string="Van Stock / Spares Return Challan")
    pending_notes = fields.Text(string="Other Pending Matters")
    handover_file = fields.Binary(string="Signed Handover Note", attachment=True)
    handover_filename = fields.Char(string="Handover Note Filename")
    state = fields.Selection(
        [("draft", "Draft"), ("handed", "Handed Over"), ("accepted", "Accepted by Successor")],
        default="draft",
        required=True,
        tracking=True,
    )
    handed_on = fields.Datetime(string="Handed Over On", readonly=True)
    handed_by_id = fields.Many2one("res.users", string="Handed Over By", readonly=True)
    accepted_on = fields.Datetime(string="Accepted On", readonly=True)
    accepted_by_id = fields.Many2one("res.users", string="Accepted By", readonly=True)

    _exit_unique = models.Constraint("UNIQUE (exit_id)", "An exit has one knowledge handover.")

    @api.depends("exit_id")
    def _compute_name(self):
        for rec in self:
            rec.name = "EXH/%s" % (rec.exit_id.name or "?")

    @api.constrains("exit_id", "successor_id")
    def _check_handover(self):
        for rec in self.sudo():
            if rec.exit_id.state == "cancelled":
                raise ValidationError(
                    "Exit %s is cancelled: there is no handover." % rec.exit_id.name
                )
            if rec.successor_id == rec.exit_id.employee_id:
                raise ValidationError("The leaver cannot hand over to themselves.")

    @api.model
    def _fix_check_party_of(self, exits):
        """HR, the leaver or the leaver's line manager writes the handover."""
        if self.env.su:
            return
        user = self.env.user
        for leaver in exits.sudo().mapped("employee_id"):
            if not (
                user.has_group(OFFICER)
                or leaver.user_id == user
                or leaver.parent_id.user_id == user
            ):
                raise UserError(
                    "%s's handover is written by the leaver, their line manager or HR."
                    % leaver.name
                )

    def _fix_check_party(self):
        self._fix_check_party_of(self.sudo().mapped("exit_id"))

    @api.model_create_multi
    def create(self, vals_list):
        Exit = self.env["fix.hr.exit"]
        for vals in vals_list:
            self._fix_check_party_of(Exit.browse(vals.get("exit_id") or []))
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open():
            self._fix_check_party()
            for rec in self.filtered(lambda r: r.state != "draft"):
                changed = {
                    name
                    for name in set(self._CONTENT) & set(vals)
                    if rec._fix_guard_differs(name, vals[name], rec[name])
                }
                if changed:
                    raise UserError("Handover %s is handed over and cannot be edited." % rec.name)
        return super().write(vals)

    def action_hand_over(self):
        self._fix_check_party()
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is already handed over." % rec.name)
            exit_ = rec.sudo().exit_id
            if exit_.state not in ("draft", "notice"):
                raise UserError("Exit %s is past clearance." % exit_.name)
            if not (rec.open_work or "").strip():
                raise UserError("List the open work being handed over (or state 'none').")
            rec._guarded().write(
                {
                    "state": "handed",
                    "handed_on": fields.Datetime.now(),
                    "handed_by_id": self.env.uid,
                }
            )
            rec.sudo().message_post(body="Handed over to %s." % rec.sudo().successor_id.name)
        return True

    def action_accept(self):
        """The successor accepts; when the successor has no login, the leaver's
        line manager accepts for them. Never the leaver or who handed it over."""
        for rec in self:
            # the successor holds no right on the exit itself: read it as superuser
            srec = rec.sudo()
            if srec.state != "handed":
                raise UserError("Only a handed-over handover is accepted.")
            if self.env.su:
                acceptors = self.env.user
            else:
                successor = srec.successor_id.user_id
                manager = srec.exit_id.employee_id.parent_id.user_id
                acceptors = successor or manager
                barred = srec.exit_id.employee_id.user_id | srec.handed_by_id
                if self.env.user in barred or self.env.user not in acceptors:
                    raise UserError(
                        "%s is accepted by %s."
                        % (rec.name, ", ".join((acceptors - barred).mapped("name")) or "nobody")
                    )
            srec._guarded().write(
                {
                    "state": "accepted",
                    "accepted_on": fields.Datetime.now(),
                    "accepted_by_id": self.env.uid,
                }
            )
            srec.message_post(body="Accepted by %s." % self.env.user.name)
        return True


class FixHrExitKnowledgeHandover(models.Model):
    """HR's clearance tick waits for the accepted knowledge handover."""

    _inherit = "fix.hr.exit"

    handover_ids = fields.One2many("fix.hr.exit.handover", "exit_id", string="Knowledge Handover")

    def _fix_tick(self, tick):
        if tick == "clearance_hr":
            for rec in self:
                # who may tick, first (unchanged); then the handover
                if rec.state != "notice":
                    raise UserError("Clearance is ticked on a confirmed exit.")
                rec._hr_require(TICKS[tick], "This clearance")
                rec._hr_refuse_conflicted("clear")
                accepted = rec.sudo().handover_ids.filtered(lambda h: h.state == "accepted")
                if not accepted:
                    raise UserError(
                        "%s: the HR clearance needs the leaver's knowledge handover, accepted "
                        "by the successor (FR-HCM-036)." % rec.name
                    )
        return super()._fix_tick(tick)


# {proposal field: hr.employee field}; the number of children is proposed
# separately, since 0 is a real answer and an empty Integer reads as 0.
_PERSONAL_PROPOSALS = {
    "proposed_private_street": "private_street",
    "proposed_private_city": "private_city",
    "proposed_private_district": "private_district",
    "proposed_private_phone": "private_phone",
    "proposed_private_email": "private_email",
    "proposed_emergency_contact": "emergency_contact",
    "proposed_emergency_contact_relation": "emergency_contact_relation",
    "proposed_emergency_phone": "emergency_phone",
    "proposed_emergency_phone_alt": "emergency_phone_alt",
    "proposed_emergency_contact_address": "emergency_contact_address",
    "proposed_marital": "marital",
    "proposed_spouse_name": "spouse_name",
}


class FixHrMasterChangePersonal(models.Model):
    """Address, personal contact, emergency contact and family details go
    through the same maker-checker request as the bank and identity fields
    (FR-HCM-040/042)."""

    _inherit = "fix.hr.master.change"

    proposed_private_street = fields.Char(string="Proposed Present Address")
    proposed_private_city = fields.Char(string="Proposed Present Thana / Upazila")
    proposed_private_district = fields.Char(string="Proposed Present District")
    proposed_private_phone = fields.Char(string="Proposed Personal Phone")
    proposed_private_email = fields.Char(string="Proposed Personal Email")
    proposed_emergency_contact = fields.Char(string="Proposed Emergency Contact")
    proposed_emergency_contact_relation = fields.Selection(
        # the source field's RESOLVED list: Odoo 19 keeps a selection that was
        # extended (selection_add) as a callable, and returning `.selection`
        # itself crashes fields_get (A09 deploy check, 23 Nov 2026)
        lambda self: self.env["hr.employee"]
        ._fields["emergency_contact_relation"]
        ._description_selection(self.env),
        string="Proposed Emergency Contact Relation",
    )
    proposed_emergency_phone = fields.Char(string="Proposed Emergency Phone")
    proposed_emergency_phone_alt = fields.Char(string="Proposed Alternative Emergency Phone")
    proposed_emergency_contact_address = fields.Text(string="Proposed Emergency Contact Address")
    proposed_marital = fields.Selection(
        lambda self: self.env["hr.employee"]._fields["marital"]._description_selection(self.env),
        string="Proposed Marital Status",
    )
    proposed_spouse_name = fields.Char(string="Proposed Spouse Name")
    proposed_children = fields.Integer(string="Proposed Number of Dependent Children")
    proposed_children_set = fields.Boolean(
        string="Change the Number of Children",
        help="Tick to propose the number of children (0 is a valid answer).",
    )

    def _fix_values(self):
        out = super()._fix_values()
        for prop, target in _PERSONAL_PROPOSALS.items():
            if self[prop]:
                out[target] = self[prop]
        if self.proposed_children_set:
            out["children"] = self.proposed_children
        return out

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= set(_PERSONAL_PROPOSALS) | {"proposed_children", "proposed_children_set"}
        return locked

    def write(self, vals):
        if not self._fix_guard_open():
            frozen = (
                set(_PERSONAL_PROPOSALS) | {"proposed_children", "proposed_children_set"}
            ) & set(vals)
            if frozen and any(r.state != "draft" for r in self.filtered("id")):
                raise UserError(
                    "A submitted master change is never edited; cancel it and raise a new one."
                )
        return super().write(vals)

    @api.constrains("proposed_private_email", "proposed_children")
    def _check_personal(self):
        for rec in self:
            email = (rec.proposed_private_email or "").strip()
            if email and ("@" not in email or " " in email):
                raise ValidationError("Personal email %r is not valid." % email)
            if rec.proposed_children < 0:
                raise ValidationError("The number of children cannot be negative.")
