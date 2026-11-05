# fix_training_budget — M22: the training budget (BRU-LMS-10) and the
# training.passed hand-off.
#
# A09 workflow audit M22 §2 "Training budget (CFO): None ... missing
# (BRU-LMS-10)". Now a company holds one budget per year; every enrolment
# carries the course's seat cost; an enrolment that would take the year over
# its budget is refused unless a routed budget exception (M63, the Training
# Budget Approver, never its requester) covers that course and technician.
# No budget for the year means no budget is ruled: nothing is refused, which
# is today's behaviour. The amounts are the business's (A09 report §7).
#
# training.passed is consumed here: the passed enrolment gets its ISO 9001
# cl. 7.2 competence evidence record (a DRAFT fix.audit.evidence; it still
# needs its file and an independent acceptor) and the enrolment is stamped.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_competency import TRAINING, changed_fields, guard_first, require_group

BUDGET_APPROVER = "cd_competency.group_training_budget_approver"


class FixApprovalMatrixTraining(models.Model):
    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[("hr_training_budget", "HR: Over-Budget Training")],
        ondelete={"hr_training_budget": "cascade"},
    )


def _year_of(day):
    return (fields.Date.to_date(day) or fields.Date.today()).year


class FixTrainingBudget(models.Model):
    _name = "fix.training.budget"
    _description = "Training Budget"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "year desc, company_id"

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    year = fields.Integer(required=True, default=lambda self: fields.Date.today().year)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(string="Budget", currency_field="currency_id", tracking=True)
    consumed = fields.Monetary(
        string="Committed", currency_field="currency_id", compute="_compute_consumed"
    )
    remaining = fields.Monetary(
        string="Remaining", currency_field="currency_id", compute="_compute_consumed"
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    _one_per_year = models.Constraint(
        "UNIQUE (company_id, year)", "One training budget per company and year"
    )

    @api.depends("year", "company_id.name")
    def _compute_name(self):
        for rec in self:
            rec.name = "Training budget %s %s" % (rec.year, rec.company_id.name or "")

    @api.constrains("amount", "year")
    def _check_amount(self):
        for rec in self:
            if (rec.amount or 0.0) < 0:
                raise ValidationError("A training budget cannot be negative.")
            if not 2000 <= rec.year <= 2100:
                raise ValidationError("A budget year is a calendar year (got %s)." % rec.year)

    def _compute_consumed(self):
        Enrollment = self.env["fix.training.enrollment"].sudo()
        for rec in self:
            rec.consumed = Enrollment._fix_committed(rec.company_id, rec.year)
            rec.remaining = (rec.amount or 0.0) - rec.consumed

    @api.model
    def _fix_budget_for(self, company, year):
        return self.sudo().search([("company_id", "=", company.id), ("year", "=", year)], limit=1)


class FixTrainingBudgetException(models.Model):
    _name = "fix.training.budget.exception"
    _description = "Over-Budget Training Request"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.people.approval.mixin"]
    _order = "id desc"

    _approval_domain = "hr_training_budget"
    _approval_apply_method = "action_approve"
    _approval_group = BUDGET_APPROVER

    name = fields.Char(required=True, default="New", readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    year = fields.Integer(required=True, default=lambda self: fields.Date.today().year)
    course_id = fields.Many2one("fix.training.course", required=True, ondelete="restrict")
    employee_ids = fields.Many2many(
        "hr.employee",
        "fix_training_budget_exception_employee_rel",
        "exception_id",
        "employee_id",
        string="Technicians",
        help="The technicians the extra seats are for (empty: any technician).",
    )
    seats = fields.Integer(required=True, default=1)
    currency_id = fields.Many2one(related="course_id.currency_id")
    amount = fields.Monetary(
        string="Over-Budget Amount",
        currency_field="currency_id",
        compute="_compute_amount",
        store=True,
    )
    reason = fields.Text(string="Justification", required=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pending", "Awaiting Approval"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )
    requested_by_id = fields.Many2one("res.users", string="Requested By", readonly=True)
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True)
    approved_at = fields.Datetime(string="Approved At", readonly=True)
    enrollment_ids = fields.One2many(
        "fix.training.enrollment", "budget_exception_id", string="Enrolments"
    )
    seats_used = fields.Integer(compute="_compute_seats_used")
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    _TERMS = frozenset({"company_id", "year", "course_id", "employee_ids", "seats", "reason"})

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "requested_by_id",
            "approved_by_id",
            "approved_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(rec.state != "draft" for rec in self):
            locked = locked | self._TERMS
        return locked

    @api.depends("seats", "course_id.cost_per_seat")
    def _compute_amount(self):
        for rec in self:
            rec.amount = (rec.seats or 0) * (rec.course_id.cost_per_seat or 0.0)

    @api.depends("enrollment_ids")
    def _compute_seats_used(self):
        for rec in self:
            rec.seats_used = len(rec.sudo().enrollment_ids)

    @api.constrains("seats")
    def _check_seats(self):
        for rec in self:
            if rec.seats <= 0:
                raise ValidationError("An over-budget request is for at least one seat.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.training.budget.exception")
                    or "TBX/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        guard_first(self, vals)
        if not self._fix_guard_open():
            frozen = changed_fields(self.filtered(lambda r: r.state != "draft"), vals, self._TERMS)
            if frozen:
                raise UserError(
                    "A requested or decided over-budget request keeps its terms (%s)."
                    % ", ".join(sorted(frozen))
                )
        return super().write(vals)

    # ---- approval declarations ---------------------------------------------
    def _approval_amount(self) -> float:
        return float(self.amount or 0.0)

    def _approval_subject_employees(self):
        return self.mapped("employee_ids")

    def _approval_preparers(self):
        return self.mapped("requested_by_id")

    def _approval_needed(self) -> bool:
        return self.state in ("draft", "pending")

    def _approval_on_rejected(self, comment):
        for rec in self:
            rec._guarded().write({"state": "rejected"})

    def action_request_approval(self, justification=None):
        require_group(self.env, TRAINING, "Requesting an over-budget enrolment")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft over-budget request is sent for approval.")
            if not (rec.reason or "").strip():
                raise UserError("Justify the over-budget training.")
            rec._guarded().write({"state": "pending", "requested_by_id": self.env.user.id})
        return super().action_request_approval(justification=justification)

    def action_recall_approval(self):
        result = super().action_recall_approval()
        self._guarded().write({"state": "draft"})
        return result

    def action_approve(self):
        """Run by the approval engine from the Training Budget Approver's task."""
        self._approval_assert_routed()
        self._people_assert_not_conflicted()
        for rec in self:
            if rec.state != "pending":
                raise UserError("%s is not awaiting a decision." % rec.name)
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": rec._people_decider().id,
                    "approved_at": fields.Datetime.now(),
                }
            )
        return True

    def action_cancel(self):
        require_group(self.env, TRAINING, "Cancelling an over-budget request")
        for rec in self:
            if rec.state not in ("draft", "pending"):
                raise UserError("Only an undecided over-budget request is cancelled.")
            if rec.approval_state == "pending":
                rec._approval_void("the request was cancelled")
            rec._guarded().write({"state": "cancelled"})
        return True

    def _fix_covers(self, course, employee, company, year, taken=None):
        """An approved request with a seat left for this course and technician.
        `taken` counts seats already given out in the same batch."""
        taken = taken or {}
        for rec in self.sudo().search(
            [
                ("state", "=", "approved"),
                ("course_id", "=", course.id),
                ("company_id", "=", company.id),
                ("year", "=", year),
            ],
            order="id",
        ):
            if rec.employee_ids and employee not in rec.employee_ids:
                continue
            if rec.seats_used + taken.get(rec.id, 0) < rec.seats:
                return rec
        return self.browse()


class FixTrainingEnrollmentBudget(models.Model):
    _inherit = "fix.training.enrollment"

    currency_id = fields.Many2one(related="course_id.currency_id")
    cost = fields.Monetary(string="Seat Cost", currency_field="currency_id", readonly=True)
    budget_year = fields.Integer(string="Budget Year", readonly=True)
    budget_exception_id = fields.Many2one(
        "fix.training.budget.exception",
        string="Over-Budget Approval",
        readonly=True,
        ondelete="restrict",
    )
    evidence_id = fields.Many2one(
        "fix.audit.evidence", string="Competence Evidence", readonly=True, ondelete="set null"
    )
    evidence_recorded_at = fields.Datetime(string="Evidence Recorded At", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "cost",
            "budget_year",
            "budget_exception_id",
            "evidence_id",
            "evidence_recorded_at",
        }

    @api.model
    def _fix_committed(self, company, year):
        rows = self.sudo()._read_group(
            [("company_id", "=", company.id), ("budget_year", "=", year)], [], ["cost:sum"]
        )
        return float(rows[0][0] or 0.0) if rows else 0.0

    @api.model_create_multi
    def create(self, vals_list):
        """BRU-LMS-10: every enrolment commits its seat cost to the year's
        budget; past the budget it needs an approved over-budget request."""
        Course = self.env["fix.training.course"].sudo()
        Budget = self.env["fix.training.budget"]
        Exception_ = self.env["fix.training.budget.exception"]
        year = fields.Date.context_today(self).year
        pending = {}
        taken = {}
        prepared = []
        for vals in vals_list:
            course = Course.browse(vals.get("course_id")).exists()
            company = (
                self.env["res.company"].browse(vals["company_id"])
                if vals.get("company_id")
                else self.env.company
            )
            cost = float(course.cost_per_seat or 0.0) if course else 0.0
            extra = {"cost": cost, "budget_year": year}
            budget = Budget._fix_budget_for(company, year) if cost > 0 else Budget.browse()
            if budget:
                key = (company.id, year)
                committed = pending.get(key)
                if committed is None:
                    committed = self._fix_committed(company, year)
                if committed + cost > (budget.amount or 0.0) + 0.005:
                    employee = self.env["hr.employee"].sudo().browse(vals.get("employee_id"))
                    cover = Exception_._fix_covers(course, employee, company, year, taken)
                    if not cover:
                        raise UserError(
                            "BRU-LMS-10: enrolling %s on %s (%.2f) takes the %s training "
                            "budget over its %.2f (%.2f committed). Request an over-budget "
                            "approval for this course first."
                            % (
                                employee.name,
                                course.name,
                                cost,
                                year,
                                budget.amount,
                                committed,
                            )
                        )
                    extra["budget_exception_id"] = cover.id
                    taken[cover.id] = taken.get(cover.id, 0) + 1
                pending[key] = committed + cost
            prepared.append((vals, extra))
        # The caller's values go through the guard as they are (state and
        # the result stamps stay refused); the cost fields are set after.
        records = super().create([vals for vals, _extra in prepared])
        for rec, (_vals, extra) in zip(records, prepared, strict=True):
            rec._guarded().write(extra)
        return records

    # ---- training.passed (consumer) ----------------------------------------------
    @api.model
    def consume_training_passed(self, event):
        """training.passed: record the passed enrolment's ISO 9001 cl. 7.2
        competence evidence and stamp the enrolment. Idempotent."""
        enr = self.sudo().browse(int(event.get("aggregate_id") or 0)).exists()
        if not enr or enr.state != "passed" or enr.evidence_id:
            return False
        asmt = enr.assessment_id
        evidence = (
            self.env["fix.audit.evidence"]
            .sudo()
            .create(
                {
                    "company_id": enr.company_id.id,
                    "evidence_type": "skills_audit",
                    "standard_ref": "ISO 9001:2015 cl. 7.2 (training and assessment)",
                    "employee_id": enr.employee_id.id,
                    "collected_on": enr.completed_on or fields.Date.today(),
                    "reference": "Training %s / enrolment %d" % (enr.course_id.code, enr.id),
                    "notes": "Passed %s on %s%s. Draft: attach the training record and have "
                    "it accepted by an independent verifier."
                    % (
                        enr.course_id.name,
                        enr.completed_on or "",
                        "; assessment %s (score %s)" % (asmt.name, asmt.score) if asmt else "",
                    ),
                }
            )
        )
        enr._guarded().write(
            {"evidence_id": evidence.id, "evidence_recorded_at": fields.Datetime.now()}
        )
        return True
