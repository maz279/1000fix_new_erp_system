# fix_m57_capture — M57 capture audit (2026-11-17): the records the M57
# sub-module pages could not capture because they did not exist.
#
#   * fix.kpi.definition (FR-PIC-006 P0, T-01, BRU-PIC-04): an employee KPI as
#     versioned, effective-dated configuration, approved by an HR Manager who
#     neither prepared nor submitted it. The technician scorecard reads the
#     definitions in force for its period and shows each value against its
#     target and threshold. Pay is NOT changed by a definition: the composite
#     and the bands stay the governed scheme's (spec 16.3: what is rewarded is
#     a business decision).
#   * fix.performance.review.cycle (FR-PIC-016/017, AUT-PIC-11): a review cycle
#     with a population and stage deadlines; opening it raises one review per
#     employee who has a line manager; a daily job chases overdue stages.
#   * fix.performance.feedback (FR-PIC-020): a multi-source feedback request on
#     a review; only the respondent answers it; the subject never reads who
#     said what (T-10), the review shows the count and the average.
#   * fix.performance.calibration.session (+ line) (FR-PIC-021, BRU-PIC-13): a
#     calibration session over one period's ratings, with the distribution
#     before and after, adjustments with reasons, concluded by someone who is
#     neither the manager nor the employee of any adjusted rating. A review is
#     not closed while a session over its period is open.
#   * fix.incentive.adjustment (FR-PIC-033/034, BRU-PIC-10/11, T-06): a manual
#     change to an employee's incentive, with a reason (and evidence for a
#     fraud reversal), approved through the routed M63 request by an Incentive
#     Approver who neither raised it nor is its subject; the employee is told
#     when it is approved, before it is applied; it becomes a visible line of
#     the next computation of its period, never of an approved period.
#   * fix.compensation.cycle (FR-PIC-038, BRU-PIC-17): a salary review cycle
#     with a budget and guidelines. A proposal raised in the cycle's window
#     belongs to it, and a proposal that would take the cycle over budget is
#     routed to (and only decided by) the CFO.
import re
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

from .fix_incentive_scheme import CFO
from .fix_performance import (
    APPROVER,
    CALIBRATOR,
    COMPENSATION,
    HR_MANAGER,
    OFFICER,
    PERIOD_RE,
    changed_fields,
    guard_first,
    period_bounds,
    require_group,
)
from .fix_performance_ops import _is_hr, _require_hr, _require_hr_or_officer, _user_of

# ---------------------------------------------------------------- KPI definition
MEASURES = [
    ("jobs_completed", "Jobs Completed"),
    ("first_time_fix", "First-Time Fix Rate"),
    ("sla_hit", "SLA Compliance"),
    ("csat", "Customer Satisfaction"),
    ("rework_rate", "Rework Rate"),
    ("rework_30d_rate", "30-Day Repeat Repair Rate"),
]
# The scorecard field each measure reads; rates are stored 0-1 and shown in %.
MEASURE_FIELD = {
    "jobs_completed": "facts_orders",
    "first_time_fix": "first_time_fix",
    "sla_hit": "sla_hit",
    "csat": "csat",
    "rework_rate": "rework_rate",
    "rework_30d_rate": "rework_30d_rate",
}
VOLUME_MEASURES = frozenset({"jobs_completed"})
MEASURE_SOURCE = {
    "jobs_completed": "M01 service orders completed in the period",
    "first_time_fix": "M01 service orders and their work orders and reworks",
    "sla_hit": "M01 service-order resolution deadlines",
    "csat": "M34 customer survey ratings of the orders",
    "rework_rate": "M01 rework orders raised against the period's orders",
    "rework_30d_rate": "M01 rework orders raised within 30 days",
}
LOWER_IS_BETTER = frozenset({"rework_rate", "rework_30d_rate"})
ROLE_PROFILES = [
    ("field_technician", "Field Technician"),
    ("workshop_technician", "Workshop Technician"),
    ("front_desk", "Front Desk / Branch"),
    ("contact_centre", "Contact Centre Agent"),
]


class FixKpiDefinition(models.Model):
    _name = "fix.kpi.definition"
    _description = "Employee KPI Definition"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "role_profile, code, date_from desc, version_no desc"

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    role_profile = fields.Selection(ROLE_PROFILES, required=True, default="field_technician")
    measure = fields.Selection(MEASURES, required=True)
    kind = fields.Selection(
        [("volume", "Volume"), ("quality", "Quality")], compute="_compute_kind", store=True
    )
    source_module = fields.Char(string="Fact Source", compute="_compute_kind", store=True)
    formula = fields.Text(
        required=True, help="How the value is worked out, in words the employee can follow."
    )
    unit = fields.Selection([("pct", "%"), ("count", "Count")], compute="_compute_kind", store=True)
    direction = fields.Selection(
        [("higher", "Higher is better"), ("lower", "Lower is better")],
        compute="_compute_kind",
        store=True,
    )
    target = fields.Float(required=True)
    threshold = fields.Float(
        required=True, help="Below this (above it, when lower is better) the KPI is breached."
    )
    version_no = fields.Integer(string="Version", readonly=True, copy=False)
    date_from = fields.Date(string="Effective From", required=True)
    date_to = fields.Date(string="Effective To", readonly=True, copy=False)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )
    submitted_by_id = fields.Many2one("res.users", string="Submitted By", readonly=True)
    submitted_at = fields.Datetime(string="Submitted At", readonly=True)
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True)
    approved_at = fields.Datetime(string="Approved At", readonly=True)
    rejection_reason = fields.Text(readonly=True)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    _TERMS = frozenset(
        {
            "name",
            "code",
            "company_id",
            "role_profile",
            "measure",
            "formula",
            "target",
            "threshold",
            "date_from",
        }
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "version_no",
            "date_to",
            "state",
            "submitted_by_id",
            "submitted_at",
            "approved_by_id",
            "approved_at",
            "rejection_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(rec.state != "draft" for rec in self):
            locked = locked | self._TERMS
        return locked

    @api.depends("measure")
    def _compute_kind(self):
        for rec in self:
            m = rec.measure
            rec.kind = "volume" if m in VOLUME_MEASURES else ("quality" if m else False)
            rec.source_module = MEASURE_SOURCE.get(m, False)
            rec.unit = "count" if m in VOLUME_MEASURES else ("pct" if m else False)
            rec.direction = "lower" if m in LOWER_IS_BETTER else ("higher" if m else False)

    @api.constrains("measure", "target", "threshold")
    def _check_figures(self):
        for rec in self:
            if rec.target < 0 or rec.threshold < 0:
                raise ValidationError("A KPI target and threshold are not negative.")
            if rec.measure not in VOLUME_MEASURES and (rec.target > 100 or rec.threshold > 100):
                raise ValidationError("A rate KPI's target and threshold are percentages (0-100).")
            if rec.measure in LOWER_IS_BETTER and rec.threshold < rec.target:
                raise ValidationError(
                    "Lower is better for %s: the threshold (the worst accepted) is at or "
                    "above the target." % rec.name
                )
            if rec.measure and rec.measure not in LOWER_IS_BETTER and rec.threshold > rec.target:
                raise ValidationError(
                    "Higher is better for %s: the threshold (the least accepted) is at or "
                    "below the target." % rec.name
                )

    # ---- writes ----------------------------------------------------------------
    def _fix_assert_preparer(self, what):
        if not (self.env.su or self.env.user.has_group(OFFICER) or _is_hr(self.env)):
            raise AccessError("%s is done by an Incentive Officer or an HR Manager." % what)

    @api.model_create_multi
    def create(self, vals_list):
        self._fix_assert_preparer("Defining a KPI")
        for vals in vals_list:
            if vals.get("code"):
                vals["code"] = vals["code"].strip().upper()
        recs = super().create(vals_list)
        for rec in recs:
            last = self.sudo().search(
                [
                    ("id", "!=", rec.id),
                    ("code", "=", rec.code),
                    ("role_profile", "=", rec.role_profile),
                    ("company_id", "=", rec.company_id.id),
                ],
                order="version_no desc",
                limit=1,
            )
            rec._guarded().write({"version_no": (last.version_no or 0) + 1})
        return recs

    def write(self, vals):
        guard_first(self, vals)
        if not self._fix_guard_open():
            self._fix_assert_preparer("Changing a KPI definition")
            frozen = changed_fields(self.filtered(lambda r: r.state != "draft"), vals, self._TERMS)
            if frozen:
                raise UserError(
                    "A submitted or approved KPI definition keeps its terms (%s); a change "
                    "is a new version." % ", ".join(sorted(frozen))
                )
        return super().write(vals)

    def unlink(self):
        if not self.env.su and any(rec.state != "draft" for rec in self):
            raise UserError("Only a draft KPI definition is deleted; an approved one is history.")
        return super().unlink()

    # ---- transitions -----------------------------------------------------------
    def action_submit(self):
        self._fix_assert_preparer("Submitting a KPI definition")
        for rec in self:
            if rec.state not in ("draft", "rejected"):
                raise UserError("%s is not a draft." % rec.display_name)
            rec._guarded().write(
                {
                    "state": "submitted",
                    "submitted_by_id": self.env.user.id,
                    "submitted_at": fields.Datetime.now(),
                    "rejection_reason": False,
                }
            )
        return True

    def _fix_assert_approver(self):
        require_group(self.env, HR_MANAGER, "Approving a KPI definition")
        for rec in self:
            if self.env.su:
                continue
            if self.env.user in (rec.create_uid | rec.submitted_by_id):
                raise UserError(
                    "The HR Manager who approves %s neither prepared nor submitted it."
                    % rec.display_name
                )

    def _fix_in_force(self, on_date, role=None, measure=None):
        """Approved definitions of this company in force on `on_date`."""
        domain = [
            ("state", "=", "approved"),
            ("date_from", "<=", on_date),
            "|",
            ("date_to", "=", False),
            ("date_to", ">=", on_date),
        ]
        if role:
            domain.append(("role_profile", "=", role))
        if measure:
            domain.append(("measure", "=", measure))
        return self.sudo().search(domain)

    def action_approve(self):
        """T-01: approving a new version closes the one in force the day before
        it takes effect; a past version is never changed retrospectively."""
        self._fix_assert_approver()
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state != "submitted":
                raise UserError("%s is not submitted." % rec.display_name)
            olds = self.sudo().search(
                [
                    ("id", "!=", rec.id),
                    ("state", "=", "approved"),
                    ("code", "=", rec.code),
                    ("role_profile", "=", rec.role_profile),
                    ("company_id", "=", rec.company_id.id),
                    "|",
                    ("date_to", "=", False),
                    ("date_to", ">=", rec.date_from),
                ]
            )
            if olds and rec.date_from < today:
                raise UserError(
                    "BRU-PIC-02: a replacement KPI version takes effect from today or later "
                    "(%s is in the past); a period already measured keeps its definition."
                    % rec.date_from
                )
            for old in olds:
                if old.date_from >= rec.date_from:
                    raise UserError(
                        "%s already starts on %s; a new version starts after it."
                        % (old.display_name, old.date_from)
                    )
                old._guarded().write({"date_to": rec.date_from - timedelta(days=1)})
            if rec.kind == "volume":
                quality = rec._fix_in_force(rec.date_from, role=rec.role_profile).filtered(
                    lambda d, rec=rec: d.kind == "quality" and d.company_id == rec.company_id
                )
                if not quality:
                    raise UserError(
                        "BRU-PIC-04: a volume KPI is approved only alongside a quality KPI for "
                        "the same role in force on %s. Approve the quality KPI first."
                        % rec.date_from
                    )
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.user.id,
                    "approved_at": fields.Datetime.now(),
                }
            )
            publish(
                self.env,
                "kpi.definition.approved",
                self._name,
                rec.id,
                {"code": rec.code, "version": rec.version_no, "from": str(rec.date_from)},
            )
        return True

    def action_reject(self, reason=None):
        self._fix_assert_approver()
        reason = (reason or "").strip()
        if not reason:
            raise UserError("Say why the KPI definition is rejected.")
        for rec in self:
            if rec.state != "submitted":
                raise UserError("%s is not submitted." % rec.display_name)
            rec._guarded().write({"state": "rejected", "rejection_reason": reason})
        return True

    def action_retire(self, retire_on=None):
        """An HR Manager ends an approved definition from a date (today or later)."""
        require_group(self.env, HR_MANAGER, "Retiring a KPI definition")
        day = fields.Date.to_date(retire_on) if retire_on else fields.Date.context_today(self)
        if day < fields.Date.context_today(self):
            raise UserError("A KPI definition is retired from today or later, never backdated.")
        for rec in self:
            if rec.state != "approved" or (rec.date_to and rec.date_to < day):
                raise UserError("%s is not in force on %s." % (rec.display_name, day))
            if day < rec.date_from:
                raise UserError("%s only starts on %s." % (rec.display_name, rec.date_from))
            rec._guarded().write({"date_to": day})
        return True

    @api.depends("code", "version_no", "name")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "%s v%s %s" % (rec.code or "", rec.version_no or 1, rec.name or "")


class FixPerformanceScorecardKpi(models.Model):
    _inherit = "fix.performance.scorecard"

    kpi_attainment = fields.Text(
        string="KPI Attainment", compute="_compute_kpi_attainment", compute_sudo=True
    )
    kpi_breaches = fields.Char(
        string="KPIs Below Threshold", compute="_compute_kpi_attainment", compute_sudo=True
    )

    @api.depends(
        "period",
        "facts_orders",
        "first_time_fix",
        "sla_hit",
        "csat",
        "rework_rate",
        "rework_30d_rate",
    )
    def _compute_kpi_attainment(self):
        Kpi = self.env["fix.kpi.definition"]
        for rec in self:
            rows, breaches = [], []
            if rec.period and PERIOD_RE.match(rec.period):
                _start, end = period_bounds(rec.period)
                for kpi in Kpi._fix_in_force(end, role="field_technician").filtered(
                    lambda d, rec=rec: d.company_id == rec.company_id
                ):
                    raw = rec[MEASURE_FIELD[kpi.measure]] or 0.0
                    value = raw if kpi.unit == "count" else round(raw * 100.0, 1)
                    lower = kpi.direction == "lower"
                    meets = value <= kpi.target if lower else value >= kpi.target
                    breached = value > kpi.threshold if lower else value < kpi.threshold
                    status = (
                        "meets target"
                        if meets
                        else ("BELOW THRESHOLD" if breached else "below target")
                    )
                    unit = "" if kpi.unit == "count" else "%"
                    rows.append(
                        "%s %s: %s%s (target %s%s, threshold %s%s) - %s"
                        % (
                            kpi.code,
                            kpi.name,
                            value,
                            unit,
                            kpi.target,
                            unit,
                            kpi.threshold,
                            unit,
                            status,
                        )
                    )
                    if breached:
                        breaches.append(kpi.code)
            rec.kpi_attainment = "\n".join(rows) or "No approved KPI definition in force."
            rec.kpi_breaches = ", ".join(breaches) or False


# ---------------------------------------------------------------- review cycle
CYCLE_TYPES = [
    ("probation", "Probation"),
    ("quarterly", "Quarterly"),
    ("half_yearly", "Half-Yearly"),
    ("annual", "Annual"),
]


class FixPerformanceReviewCycle(models.Model):
    _name = "fix.performance.review.cycle"
    _description = "Performance Review Cycle"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "self_deadline desc, id desc"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    cycle_type = fields.Selection(CYCLE_TYPES, required=True, default="annual")
    period = fields.Char(
        required=True,
        help="The period the reviews cover, written as the reviews are: YYYY-MM, YYYY-Qn, "
        "YYYY-Hn or YYYY.",
    )
    department_id = fields.Many2one("hr.department", string="Department")
    employee_ids = fields.Many2many(
        "hr.employee",
        "fix_review_cycle_employee_rel",
        "cycle_id",
        "employee_id",
        string="Named Employees",
        help="Empty: every active employee of the company (or of the department).",
    )
    probation_until = fields.Date(
        string="Probation Ending By",
        help="Probation cycles: employees whose active contract's probation ends between "
        "today and this date.",
    )
    self_deadline = fields.Date(string="Self-Assessment Due", required=True)
    manager_deadline = fields.Date(string="Manager Assessment Due", required=True)
    calibration_deadline = fields.Date(string="Calibration Due", required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("open", "Open"), ("closed", "Closed")],
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )
    review_ids = fields.One2many("fix.performance.review", "cycle_id", string="Reviews")
    review_count = fields.Integer(compute="_compute_progress", string="Reviews")
    closed_count = fields.Integer(compute="_compute_progress", string="Closed Reviews")
    overdue_count = fields.Integer(compute="_compute_progress", string="Overdue Reviews")
    skipped_note = fields.Text(string="Not Raised", readonly=True)
    opened_by_id = fields.Many2one("res.users", string="Opened By", readonly=True)
    opened_at = fields.Datetime(string="Opened At", readonly=True)
    closed_by_id = fields.Many2one("res.users", string="Closed By", readonly=True)
    closed_at = fields.Datetime(string="Closed At", readonly=True)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    _TERMS = frozenset(
        {
            "name",
            "company_id",
            "cycle_type",
            "period",
            "department_id",
            "employee_ids",
            "probation_until",
            "self_deadline",
            "manager_deadline",
            "calibration_deadline",
        }
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "skipped_note",
            "opened_by_id",
            "opened_at",
            "closed_by_id",
            "closed_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(rec.state != "draft" for rec in self):
            locked = locked | self._TERMS
        return locked

    @api.depends("review_ids.state", "self_deadline", "manager_deadline")
    def _compute_progress(self):
        today = fields.Date.context_today(self)
        for rec in self:
            reviews = rec.sudo().review_ids
            rec.review_count = len(reviews)
            rec.closed_count = len(reviews.filtered(lambda r: r.state == "closed"))
            rec.overdue_count = len(rec._fix_overdue(reviews, today))

    def _fix_overdue(self, reviews, today):
        self.ensure_one()
        return reviews.filtered(
            lambda r: (
                (r.state in ("draft", "self_review") and self.self_deadline < today)
                or (
                    r.state == "manager_review"
                    and r.approval_state != "pending"
                    and self.manager_deadline < today
                )
            )
        )

    @api.constrains("period")
    def _check_period(self):
        for rec in self:
            if not re.match(r"^\d{4}(-(0[1-9]|1[0-2]|Q[1-4]|H[12]))?$", rec.period or ""):
                raise ValidationError(
                    "A review period is written YYYY-MM, YYYY-Qn, YYYY-Hn or YYYY (got %r)."
                    % (rec.period or "")
                )

    @api.constrains("self_deadline", "manager_deadline", "calibration_deadline")
    def _check_deadlines(self):
        for rec in self:
            if not (rec.self_deadline <= rec.manager_deadline <= rec.calibration_deadline):
                raise ValidationError(
                    "The stages run in order: self-assessment, then the manager's, then "
                    "calibration."
                )

    @api.model_create_multi
    def create(self, vals_list):
        _require_hr_or_officer(self.env, "Setting up a review cycle")
        return super().create(vals_list)

    def write(self, vals):
        guard_first(self, vals)
        if not self._fix_guard_open():
            _require_hr_or_officer(self.env, "Changing a review cycle")
            frozen = changed_fields(self.filtered(lambda r: r.state != "draft"), vals, self._TERMS)
            if frozen:
                raise UserError(
                    "An open review cycle keeps its population, period and deadlines (%s)."
                    % ", ".join(sorted(frozen))
                )
        return super().write(vals)

    def unlink(self):
        if not self.env.su and any(rec.state != "draft" for rec in self):
            raise UserError("Only a draft review cycle is deleted.")
        return super().unlink()

    def _fix_population(self):
        self.ensure_one()
        Emp = self.env["hr.employee"].sudo()
        if self.employee_ids:
            return self.employee_ids.sudo().filtered("active")
        if self.cycle_type == "probation":
            if not self.probation_until:
                raise UserError("Say by when the probations end (Probation Ending By).")
            today = fields.Date.context_today(self)
            contracts = (
                self.env["fix.employment.contract"]
                .sudo()
                .search(
                    [
                        ("company_id", "=", self.company_id.id),
                        ("state", "=", "active"),
                        ("probation_end", ">=", today),
                        ("probation_end", "<=", self.probation_until),
                    ]
                )
            )
            return contracts.mapped("employee_id").filtered("active")
        domain = [("company_id", "=", self.company_id.id), ("active", "=", True)]
        if self.department_id:
            domain.append(("department_id", "child_of", self.department_id.id))
        return Emp.search(domain)

    def action_open(self):
        """HR opens the cycle: one review per employee of the population who
        has a line manager to review them (FR-PIC-016)."""
        _require_hr_or_officer(self.env, "Opening a review cycle")
        Review = self.env["fix.performance.review"]
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is already open." % rec.name)
            people = rec._fix_population()
            if not people:
                raise UserError("%s has nobody in its population." % rec.name)
            skipped, vals_list = [], []
            for emp in people:
                if not emp.parent_id:
                    skipped.append("%s: no line manager" % emp.name)
                    continue
                if Review.sudo().search_count(
                    [
                        ("employee_id", "=", emp.id),
                        ("period", "=", rec.period),
                        ("company_id", "=", rec.company_id.id),
                    ]
                ):
                    skipped.append("%s: already has a %s review" % (emp.name, rec.period))
                    continue
                vals_list.append(
                    {
                        "employee_id": emp.id,
                        "reviewer_id": emp.parent_id.id,
                        "period": rec.period,
                        "company_id": rec.company_id.id,
                        "cycle_id": rec.id,
                    }
                )
            if not vals_list:
                raise UserError("%s would raise no review:\n%s" % (rec.name, "\n".join(skipped)))
            Review._guarded().create(vals_list)
            rec._guarded().write(
                {
                    "state": "open",
                    "opened_by_id": self.env.user.id,
                    "opened_at": fields.Datetime.now(),
                    "skipped_note": "\n".join(skipped) or False,
                }
            )
        return True

    def action_close(self):
        _require_hr(self.env, "Closing a review cycle")
        for rec in self:
            if rec.state != "open":
                raise UserError("%s is not open." % rec.name)
            pending = rec.sudo().review_ids.filtered(lambda r: r.state != "closed")
            if pending:
                raise UserError(
                    "%s still has %d review(s) not closed (%s)."
                    % (rec.name, len(pending), ", ".join(pending[:5].mapped("employee_id.name")))
                )
            rec._guarded().write(
                {
                    "state": "closed",
                    "closed_by_id": self.env.user.id,
                    "closed_at": fields.Datetime.now(),
                }
            )
        return True

    @api.model
    def _cron_chase_overdue(self):
        """AUT-PIC-11: a to-do to whoever holds an overdue stage, and to their
        own manager (the next level) once it is overdue."""
        today = fields.Date.context_today(self)
        for cycle in self.sudo().search([("state", "=", "open")]):
            for review in cycle._fix_overdue(cycle.review_ids, today):
                late = review.state in ("draft", "self_review")
                who = review.employee_id if late else review.reviewer_id
                summary = "Overdue %s: %s" % (
                    "self-assessment" if late else "manager assessment",
                    review.name,
                )
                for user in (_user_of(who), _user_of(who.parent_id) if who.parent_id else None):
                    if not user or not user.active:
                        continue
                    if review.activity_ids.filtered(
                        lambda a, u=user, s=summary: a.user_id == u and a.summary == s
                    ):
                        continue
                    review.activity_schedule(
                        "mail.mail_activity_data_todo",
                        date_deadline=today,
                        summary=summary,
                        user_id=user.id,
                    )
        return True


# ---------------------------------------------------------------- review extension
class FixPerformanceReviewCapture(models.Model):
    # mail.activity.mixin: the AUT-PIC-11 chase gives the overdue party a to-do.
    _name = "fix.performance.review"
    _inherit = ["fix.performance.review", "mail.activity.mixin"]

    cycle_id = fields.Many2one(
        "fix.performance.review.cycle",
        string="Cycle",
        readonly=True,
        index=True,
        ondelete="restrict",
    )
    feedback_ids = fields.One2many("fix.performance.feedback", "review_id", string="Feedback")
    feedback_count = fields.Integer(
        string="Feedback Received", compute="_compute_feedback", compute_sudo=True
    )
    feedback_avg = fields.Float(
        string="Feedback Average (1-5)", compute="_compute_feedback", compute_sudo=True
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"cycle_id"}

    @api.depends("feedback_ids.state", "feedback_ids.rating")
    def _compute_feedback(self):
        for rec in self:
            done = rec.feedback_ids.filtered(lambda f: f.state == "submitted")
            rec.feedback_count = len(done)
            rec.feedback_avg = round(sum(done.mapped("rating")) / len(done), 2) if done else 0.0

    def action_close(self):
        """BRU-PIC-13: a review is not finalised while a calibration session over
        its period is still open."""
        Session = self.env["fix.performance.calibration.session"].sudo()
        for rec in self:
            open_sessions = Session.search(
                [
                    ("period", "=", rec.period),
                    ("company_id", "=", rec.company_id.id),
                    ("state", "in", ("draft", "in_session")),
                ]
            ).filtered(lambda s, rec=rec: not s.cycle_id or s.cycle_id == rec.cycle_id)
            if open_sessions:
                raise UserError(
                    "BRU-PIC-13: %s is in calibration session %s; close it after the session "
                    "concludes." % (rec.name, open_sessions[0].name)
                )
        return super().action_close()


# ---------------------------------------------------------------- feedback
RELATIONSHIPS = [
    ("peer", "Peer"),
    ("subordinate", "Subordinate"),
    ("cross_functional", "Cross-Functional Colleague"),
    ("skip_manager", "Manager's Manager"),
]


class FixPerformanceFeedback(models.Model):
    _name = "fix.performance.feedback"
    _description = "Multi-Source Feedback"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(readonly=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    review_id = fields.Many2one(
        "fix.performance.review", required=True, ondelete="cascade", index=True
    )
    employee_id = fields.Many2one(
        related="review_id.employee_id", string="About", store=True, index=True
    )
    period = fields.Char(related="review_id.period", store=True)
    respondent_id = fields.Many2one("hr.employee", string="Respondent", required=True, index=True)
    relationship = fields.Selection(RELATIONSHIPS, required=True, default="peer")
    due_date = fields.Date(string="Answer By")
    rating = fields.Float(string="Rating (1-5)", readonly=True)
    strengths = fields.Text(readonly=True)
    improvements = fields.Text(string="To Improve", readonly=True)
    decline_reason = fields.Text(readonly=True)
    state = fields.Selection(
        [("requested", "Requested"), ("submitted", "Submitted"), ("declined", "Declined")],
        default="requested",
        required=True,
        tracking=True,
        index=True,
    )
    requested_by_id = fields.Many2one("res.users", string="Requested By", readonly=True)
    submitted_at = fields.Datetime(string="Answered At", readonly=True)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    _one_request = models.Constraint(
        "UNIQUE (review_id, respondent_id)", "One feedback request per respondent and review"
    )

    _TERMS = frozenset({"company_id", "review_id", "respondent_id", "relationship", "due_date"})

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "name",
            "rating",
            "strengths",
            "improvements",
            "decline_reason",
            "state",
            "requested_by_id",
            "submitted_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(rec.state != "requested" for rec in self):
            locked = locked | self._TERMS
        return locked

    @api.constrains("review_id", "respondent_id")
    def _check_respondent(self):
        for rec in self:
            review = rec.review_id.sudo()
            if rec.respondent_id == review.employee_id:
                raise ValidationError(
                    "Self-assessment is the review's own; a feedback respondent is someone else."
                )
            if rec.respondent_id == review.reviewer_id:
                raise ValidationError(
                    "The line manager gives the manager assessment; ask someone else for "
                    "feedback."
                )

    @api.model_create_multi
    def create(self, vals_list):
        _require_hr_or_officer(self.env, "Requesting multi-source feedback")
        Review = self.env["fix.performance.review"].sudo()
        for vals in vals_list:
            review = Review.browse(vals.get("review_id"))
            if review.exists() and review.state in ("calibrated", "closed"):
                raise UserError(
                    "%s is %s; feedback is gathered before calibration."
                    % (review.name, review.state)
                )
            if review.exists():
                vals["company_id"] = review.company_id.id
        recs = super().create(vals_list)
        Seq = self.env["ir.sequence"].sudo()
        for rec in recs:
            rec._guarded().write(
                {
                    "name": Seq.next_by_code("fix.performance.feedback") or "FBK/New",
                    "requested_by_id": self.env.user.id,
                }
            )
        for rec in recs:
            user = _user_of(rec.respondent_id)
            if user and user.active:
                rec.activity_schedule(
                    "mail.mail_activity_data_todo",
                    date_deadline=rec.due_date or fields.Date.context_today(self),
                    summary="Feedback requested: %s" % rec.name,
                    user_id=user.id,
                )
        return recs

    def write(self, vals):
        guard_first(self, vals)
        if not self._fix_guard_open():
            _require_hr_or_officer(self.env, "Changing a feedback request")
            frozen = changed_fields(
                self.filtered(lambda r: r.state != "requested"), vals, self._TERMS
            )
            if frozen:
                raise UserError("An answered feedback request is final.")
        return super().write(vals)

    def unlink(self):
        if not self.env.su and any(rec.state != "requested" for rec in self):
            raise UserError("Answered feedback is evidence; it is not deleted.")
        return super().unlink()

    def _fix_assert_respondent(self):
        self.check_access("read")
        for rec in self.sudo():
            if self.env.su:
                continue
            if _user_of(rec.respondent_id) != self.env.user:
                raise AccessError("Only %s answers this feedback request." % rec.respondent_id.name)
            if rec.state != "requested":
                raise UserError("%s is already answered." % rec.name)
            if rec.review_id.state in ("calibrated", "closed"):
                raise UserError("%s is past calibration; feedback is closed." % rec.review_id.name)

    def action_submit_feedback(self, feedback=None, rating=None, strengths=None, improvements=None):
        """The respondent answers. ``feedback`` is the workspace prompt's one
        string: '<rating 1-5> <comments>'."""
        self._fix_assert_respondent()
        if feedback not in (None, False, ""):
            head, _sep, tail = str(feedback).strip().partition(" ")
            try:
                rating = float(head)
            except ValueError:
                raise UserError("Answer as: <rating 1-5> <comments>.") from None
            strengths = strengths or tail.strip()
        try:
            rating = float(rating)
        except (TypeError, ValueError):
            raise UserError("A rating is a number from 1 to 5.") from None
        if not 1 <= rating <= 5:
            raise UserError("A rating is on the 1-5 scale.")
        if not (strengths or improvements):
            raise UserError("Say what the rating rests on.")
        for rec in self.sudo():
            rec._guarded().write(
                {
                    "state": "submitted",
                    "rating": rating,
                    "strengths": strengths or False,
                    "improvements": improvements or False,
                    "submitted_at": fields.Datetime.now(),
                }
            )
            rec.activity_unlink(["mail.mail_activity_data_todo"])
        return True

    def action_decline(self, reason=None):
        self._fix_assert_respondent()
        reason = (reason or "").strip()
        if not reason:
            raise UserError("Say why you decline (for example: I have not worked with them).")
        for rec in self.sudo():
            rec._guarded().write(
                {
                    "state": "declined",
                    "decline_reason": reason,
                    "submitted_at": fields.Datetime.now(),
                }
            )
            rec.activity_unlink(["mail.mail_activity_data_todo"])
        return True


# ---------------------------------------------------------------- calibration session
def rating_band(rating):
    if not rating:
        return "Not rated"
    if rating >= 4.5:
        return "5 Outstanding"
    if rating >= 3.5:
        return "4 Exceeds"
    if rating >= 2.5:
        return "3 Meets"
    if rating >= 1.5:
        return "2 Below"
    return "1 Unsatisfactory"


def distribution(ratings):
    counts = {}
    for value in ratings:
        band = rating_band(value)
        counts[band] = counts.get(band, 0) + 1
    total = sum(counts.values())
    if not total:
        return "No ratings"
    return "; ".join(
        "%s: %d (%.0f%%)" % (band, n, n * 100.0 / total)
        for band, n in sorted(counts.items(), reverse=True)
    )


class FixCalibrationSession(models.Model):
    _name = "fix.performance.calibration.session"
    _description = "Rating Calibration Session"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(readonly=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    period = fields.Char(required=True, help="The review period whose ratings are calibrated.")
    cycle_id = fields.Many2one("fix.performance.review.cycle", string="Review Cycle")
    scope = fields.Char(help="Teams or branches compared, in words.")
    session_date = fields.Date(required=True, default=fields.Date.context_today)
    participant_ids = fields.Many2many(
        "hr.employee",
        "fix_calibration_session_participant_rel",
        "session_id",
        "employee_id",
        string="Managers Taking Part",
    )
    review_ids = fields.Many2many(
        "fix.performance.review", compute="_compute_reviews", string="Ratings in Scope"
    )
    pending_count = fields.Integer(
        compute="_compute_reviews", string="Awaiting Calibration Approval"
    )
    line_ids = fields.One2many(
        "fix.performance.calibration.line", "session_id", string="Rating Changes"
    )
    distribution_before = fields.Char(readonly=True)
    distribution_after = fields.Char(readonly=True)
    minutes = fields.Text()
    state = fields.Selection(
        [("draft", "Draft"), ("in_session", "In Session"), ("concluded", "Concluded")],
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )
    started_by_id = fields.Many2one("res.users", string="Started By", readonly=True)
    concluded_by_id = fields.Many2one("res.users", string="Concluded By", readonly=True)
    concluded_at = fields.Datetime(string="Concluded At", readonly=True)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    _TERMS = frozenset({"company_id", "period", "cycle_id"})

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "name",
            "distribution_before",
            "distribution_after",
            "state",
            "started_by_id",
            "concluded_by_id",
            "concluded_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(rec.state != "draft" for rec in self):
            locked = locked | self._TERMS
        if self and any(rec.state == "concluded" for rec in self):
            locked = locked | {"scope", "session_date", "participant_ids", "minutes"}
        return locked

    def _fix_scope_reviews(self):
        self.ensure_one()
        domain = [
            ("period", "=", self.period or ""),
            ("company_id", "=", self.company_id.id),
            ("state", "in", ("manager_review", "calibrated", "closed")),
        ]
        if self.cycle_id:
            domain.append(("cycle_id", "=", self.cycle_id.id))
        return self.env["fix.performance.review"].sudo().search(domain)

    @api.depends("period", "cycle_id", "company_id")
    def _compute_reviews(self):
        for rec in self:
            reviews = rec._fix_scope_reviews()
            rec.review_ids = reviews
            rec.pending_count = len(reviews.filtered(lambda r: r.state == "manager_review"))

    @staticmethod
    def _fix_assert_role(env, what):
        if not (env.su or _is_hr(env) or env.user.has_group(CALIBRATOR)):
            raise AccessError("%s is done by HR or a Performance Calibrator." % what)

    @api.model_create_multi
    def create(self, vals_list):
        self._fix_assert_role(self.env, "Opening a calibration session")
        recs = super().create(vals_list)
        Seq = self.env["ir.sequence"].sudo()
        for rec in recs:
            rec._guarded().write(
                {"name": Seq.next_by_code("fix.performance.calibration") or "CAL/New"}
            )
        return recs

    def write(self, vals):
        guard_first(self, vals)
        if not self._fix_guard_open():
            self._fix_assert_role(self.env, "Changing a calibration session")
            if any(rec.state == "concluded" for rec in self):
                raise UserError("A concluded calibration session is the record; it is final.")
            frozen = changed_fields(self.filtered(lambda r: r.state != "draft"), vals, self._TERMS)
            if frozen:
                raise UserError("A started session keeps its period and cycle.")
        return super().write(vals)

    def unlink(self):
        if not self.env.su and any(rec.state != "draft" for rec in self):
            raise UserError("Only a draft calibration session is deleted.")
        return super().unlink()

    def action_start(self):
        """The distribution before is measured from the managers' ratings."""
        self._fix_assert_role(self.env, "Starting a calibration session")
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s has started." % rec.name)
            reviews = rec._fix_scope_reviews()
            if not reviews:
                raise UserError("No rated review of %s is in scope." % rec.period)
            rec._guarded().write(
                {
                    "state": "in_session",
                    "started_by_id": self.env.user.id,
                    "distribution_before": distribution(reviews.mapped("manager_rating")),
                }
            )
        return True

    def action_conclude(self):
        """BRU-PIC-13: every rating in scope is calibrated; the changes are
        applied; the concluder is neither the manager nor the employee of any
        changed rating."""
        self._fix_assert_role(self.env, "Concluding a calibration session")
        user = self.env.user
        for rec in self:
            if rec.state != "in_session":
                raise UserError("%s is not in session." % rec.name)
            reviews = rec._fix_scope_reviews()
            waiting = reviews.filtered(lambda r: r.state == "manager_review")
            if waiting:
                raise UserError(
                    "BRU-PIC-13: %d rating(s) in scope are not calibrated yet (%s)."
                    % (len(waiting), ", ".join(waiting[:5].mapped("name")))
                )
            for line in rec.line_ids.sudo():
                review = line.review_id
                if not self.env.su and user in (
                    _user_of(review.employee_id) | _user_of(review.reviewer_id)
                ):
                    raise UserError(
                        "You rated or are rated in %s: someone else concludes this session."
                        % review.name
                    )
                if review.state != "calibrated":
                    raise UserError(
                        "%s is %s; only a calibrated rating moves." % (review.name, review.state)
                    )
            for line in rec.line_ids.sudo():
                review = line.review_id
                old = review.calibrated_rating
                review._guarded().write({"calibrated_rating": line.new_rating})
                review.message_post(
                    body="Calibration session %s moved the rating from %s to %s: %s"
                    % (rec.name, old, line.new_rating, line.reason)
                )
                line._guarded().write({"previous_rating": old, "applied": True})
            rec._guarded().write(
                {
                    "state": "concluded",
                    "concluded_by_id": user.id,
                    "concluded_at": fields.Datetime.now(),
                    "distribution_after": distribution(
                        rec._fix_scope_reviews().mapped("calibrated_rating")
                    ),
                }
            )
        return True


class FixCalibrationLine(models.Model):
    _name = "fix.performance.calibration.line"
    _description = "Calibration Rating Change"
    _inherit = ["fix.guarded.mixin"]

    session_id = fields.Many2one(
        "fix.performance.calibration.session", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="session_id.company_id", store=True, index=True)
    review_id = fields.Many2one("fix.performance.review", required=True, ondelete="restrict")
    employee_id = fields.Many2one(related="review_id.employee_id", string="Employee")
    manager_rating = fields.Float(related="review_id.manager_rating", string="Manager Rating")
    new_rating = fields.Float(string="Calibrated Rating", required=True)
    reason = fields.Char(required=True)
    previous_rating = fields.Float(readonly=True)
    applied = fields.Boolean(readonly=True)

    _one_per_review = models.Constraint(
        "UNIQUE (session_id, review_id)", "A rating is changed once per session"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"previous_rating", "applied"}

    @api.constrains("new_rating", "review_id", "session_id")
    def _check_line(self):
        for rec in self:
            if not 1 <= rec.new_rating <= 5:
                raise ValidationError("A calibrated rating is on the 1-5 scale.")
            if rec.review_id not in rec.session_id._fix_scope_reviews():
                raise ValidationError(
                    "%s is not one of the session's ratings in scope." % rec.review_id.name
                )

    def _fix_assert_open(self, sessions):
        FixCalibrationSession._fix_assert_role(self.env, "Changing a calibration rating")
        if any(s.state != "in_session" for s in sessions):
            raise UserError("Ratings change only while the session is in session.")

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            sessions = self.env["fix.performance.calibration.session"].browse(
                [v.get("session_id") for v in vals_list]
            )
            self._fix_assert_open(sessions)
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open():
            self._fix_assert_open(self.mapped("session_id"))
        return super().write(vals)

    def unlink(self):
        if not self._fix_guard_open():
            self._fix_assert_open(self.mapped("session_id"))
        return super().unlink()


# ---------------------------------------------------------------- incentive adjustment
ADJUSTMENT_TYPES = [
    ("correction", "Correction"),
    ("fraud_reversal", "Reversal (Fraudulent or Invalid Job)"),
    ("discretionary", "Discretionary Award"),
]


class FixIncentiveAdjustment(models.Model):
    _name = "fix.incentive.adjustment"
    _description = "Incentive Adjustment"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.people.approval.mixin"]
    _order = "id desc"

    _approval_domain = "hr_incentive"
    _approval_apply_method = "action_approve"
    _approval_group = APPROVER

    name = fields.Char(readonly=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    period = fields.Char(required=True, help="YYYY-MM: the incentive run it is paid in.")
    adjustment_type = fields.Selection(ADJUSTMENT_TYPES, required=True, default="correction")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(
        currency_field="currency_id", required=True, help="Positive pays more; negative recovers."
    )
    reason = fields.Text(required=True, help="Shown to the employee on their incentive line.")
    evidence_ref = fields.Char(
        string="Evidence", help="The job, investigation or document the change rests on."
    )
    service_order_id = fields.Many2one("fix.service.order", string="Service Order")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("approved", "Approved (applies at the next computation)"),
            ("applied", "Applied"),
            ("rejected", "Rejected"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True)
    approved_at = fields.Datetime(string="Approved At", readonly=True)
    applied_run_id = fields.Many2one("fix.incentive.run", string="Applied In Run", readonly=True)
    applied_line_id = fields.Many2one(
        "fix.incentive.line", string="Applied Line", readonly=True, ondelete="set null"
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    _TERMS = frozenset(
        {
            "company_id",
            "employee_id",
            "period",
            "adjustment_type",
            "currency_id",
            "amount",
            "reason",
            "evidence_ref",
            "service_order_id",
        }
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "name",
            "state",
            "approved_by_id",
            "approved_at",
            "applied_run_id",
            "applied_line_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(rec.state != "draft" or rec.approval_state == "pending" for rec in self):
            locked = locked | self._TERMS
        return locked

    # ---- approval declarations ------------------------------------------------
    def _approval_amount(self) -> float:
        return abs(float(self.amount or 0.0))

    def _approval_preparers(self):
        return self.mapped("create_uid")

    def _approval_needed(self) -> bool:
        return self.state == "draft"

    def _approval_on_rejected(self, comment):
        for rec in self:
            rec._guarded().write({"state": "rejected"})
            rec.message_post(body="Incentive adjustment rejected: %s" % (comment or ""))

    # ---- checks ---------------------------------------------------------------
    def _fix_period_run(self):
        self.ensure_one()
        return (
            self.env["fix.incentive.run"]
            .sudo()
            .search(
                [("company_id", "=", self.company_id.id), ("period", "=", self.period)], limit=1
            )
        )

    @api.constrains("period", "amount", "adjustment_type", "evidence_ref", "reason")
    def _check_terms(self):
        for rec in self:
            if not PERIOD_RE.match(rec.period or ""):
                raise ValidationError("An adjustment's period is a month written YYYY-MM.")
            if not rec.amount:
                raise ValidationError("An adjustment changes the amount: it is not zero.")
            if not (rec.reason or "").strip():
                raise ValidationError("BRU-PIC-10: an adjustment states its reason.")
            if rec.adjustment_type == "fraud_reversal":
                if rec.amount > 0:
                    raise ValidationError("A reversal recovers incentive: its amount is negative.")
                if not (rec.evidence_ref or "").strip():
                    raise ValidationError(
                        "BRU-PIC-11: a reversal names its evidence (the job and the finding)."
                    )
            if rec.adjustment_type == "discretionary" and rec.amount < 0:
                raise ValidationError("A discretionary award is positive.")

    def _fix_assert_period_open(self):
        for rec in self:
            run = rec._fix_period_run()
            if run and run.state == "approved":
                raise UserError(
                    "T-06: the %s incentive run is approved and locked. Adjust a later period."
                    % rec.period
                )

    @api.model_create_multi
    def create(self, vals_list):
        require_group(self.env, OFFICER, "Raising an incentive adjustment")
        Emp = self.env["hr.employee"].sudo()
        for vals in vals_list:
            if not self.env.su and Emp.browse(vals.get("employee_id")).user_id == self.env.user:
                raise UserError("You cannot adjust your own incentive.")
        recs = super().create(vals_list)
        Seq = self.env["ir.sequence"].sudo()
        for rec in recs:
            rec._guarded().write(
                {"name": Seq.next_by_code("fix.incentive.adjustment") or "IAD/New"}
            )
        recs._fix_assert_period_open()
        return recs

    def write(self, vals):
        guard_first(self, vals)
        if not self._fix_guard_open():
            require_group(self.env, OFFICER, "Changing an incentive adjustment")
            frozen = changed_fields(
                self.filtered(lambda r: r.state != "draft" or r.approval_state == "pending"),
                vals,
                self._TERMS,
            )
            if frozen:
                raise UserError(
                    "An adjustment in approval or decided keeps its terms (%s)."
                    % ", ".join(sorted(frozen))
                )
        res = super().write(vals)
        if "period" in vals and not self._fix_guard_open():
            self._fix_assert_period_open()
        return res

    def unlink(self):
        if not self.env.su:
            raise UserError("An incentive adjustment is evidence; cancel it instead.")
        return super().unlink()

    # ---- transitions ----------------------------------------------------------
    def action_request_approval(self, justification=None):
        require_group(self.env, OFFICER, "Requesting an adjustment's approval")
        self._fix_assert_period_open()
        return super().action_request_approval(justification=justification)

    def action_approve(self):
        """The Incentive Approver's routed decision. The employee is told
        before the adjustment reaches their incentive (BRU-PIC-10/11)."""
        self._approval_assert_routed()
        self._people_assert_not_conflicted()
        self._fix_assert_period_open()
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is not awaiting approval." % rec.name)
            # The routed decision is the authority: the approver holds no
            # write access to adjustments (only Incentive Officers do).
            rec = rec.sudo()
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": rec._people_decider().id,
                    "approved_at": fields.Datetime.now(),
                }
            )
            note = "An incentive adjustment of %.2f BDT (%s) was approved for %s: %s" % (
                rec.amount,
                dict(ADJUSTMENT_TYPES)[rec.adjustment_type],
                rec.period,
                rec.reason,
            )
            user = _user_of(rec.employee_id)
            if user and user.active:
                rec.message_subscribe(partner_ids=user.partner_id.ids)
                rec.activity_schedule(
                    "mail.mail_activity_data_todo",
                    summary="Your incentive is adjusted (%s)" % rec.name,
                    note=note,
                    user_id=user.id,
                )
            rec.message_post(body=note)
            run = rec._fix_period_run()
            if run and run.state == "computed":
                rec.message_post(
                    body="The %s run is already computed: reset and recompute it to apply this "
                    "adjustment." % rec.period
                )
        return True

    def action_cancel(self):
        require_group(self.env, OFFICER, "Cancelling an incentive adjustment")
        for rec in self:
            if rec.state not in ("draft", "approved"):
                raise UserError("%s is %s; it is no longer cancelled." % (rec.name, rec.state))
            if rec.approval_state == "pending":
                rec._approval_void("the adjustment was cancelled")
            rec._guarded().write({"state": "cancelled"})
        return True


class FixIncentiveLineAdjustment(models.Model):
    _inherit = "fix.incentive.line"

    line_type = fields.Selection(
        selection_add=[("adjustment", "Adjustment")], ondelete={"adjustment": "cascade"}
    )
    adjustment_id = fields.Many2one(
        "fix.incentive.adjustment", string="Adjustment", readonly=True, ondelete="restrict"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"adjustment_id"}


class FixIncentiveRunAdjustment(models.Model):
    _inherit = "fix.incentive.run"

    def _fix_apply_adjustments(self):
        """Approved adjustments of the period become visible lines of the run;
        nobody's incentive in a run goes below zero."""
        self.ensure_one()
        Adj = self.env["fix.incentive.adjustment"].sudo()
        Line = self.env["fix.incentive.line"]._guarded()
        adjustments = Adj.search(
            [
                ("company_id", "=", self.company_id.id),
                ("period", "=", self.period),
                ("state", "=", "approved"),
            ],
            order="id",
        )
        lines = self.sudo().line_ids
        for adj in adjustments:
            base = lines.filtered(
                lambda line, adj=adj: line.employee_id == adj.employee_id
                and line.line_type == "incentive"
            )[:1]
            if not base:
                raise UserError(
                    "Adjustment %s: %s has no published scorecard (no line) in the %s run."
                    % (adj.name, adj.employee_id.name, self.period)
                )
            line = Line.create(
                {
                    "run_id": self.id,
                    "company_id": self.company_id.id,
                    "scorecard_id": base.scorecard_id.id,
                    "employee_id": adj.employee_id.id,
                    "line_type": "adjustment",
                    "adjustment_id": adj.id,
                    "gross_amount": adj.amount,
                    "amount": adj.amount,
                    "proration_factor": 1.0,
                    "eligible": True,
                    "eligibility_note": "adjustment %s (%s): %s"
                    % (adj.name, dict(ADJUSTMENT_TYPES)[adj.adjustment_type], adj.reason),
                    "currency_id": self.currency_id.id,
                }
            )
            lines |= line
            adj._guarded().write(
                {"state": "applied", "applied_run_id": self.id, "applied_line_id": line.id}
            )
        for employee in adjustments.mapped("employee_id"):
            total = sum(lines.filtered(lambda r, e=employee: r.employee_id == e).mapped("amount"))
            if total < -0.005:
                raise UserError(
                    "Adjustments would take %s's %s incentive below zero (%.2f): an incentive "
                    "is not turned into a wage deduction. Spread the recovery over later periods."
                    % (employee.name, self.period, total)
                )

    def action_compute(self):
        res = super().action_compute()
        for rec in self:
            rec._fix_apply_adjustments()
        return res

    def action_reset_draft(self):
        Adj = self.env["fix.incentive.adjustment"].sudo()
        for rec in self:
            Adj.search([("applied_run_id", "=", rec.id)])._guarded().write(
                {"state": "approved", "applied_run_id": False, "applied_line_id": False}
            )
        return super().action_reset_draft()


# ---------------------------------------------------------------- compensation cycle
class FixCompensationCycle(models.Model):
    _name = "fix.compensation.cycle"
    _description = "Compensation Review Cycle"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "date_from desc, id desc"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    date_from = fields.Date(string="Raises Effective From", required=True)
    date_to = fields.Date(string="Raises Effective To", required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    budget = fields.Monetary(
        string="Monthly Increase Budget",
        currency_field="currency_id",
        groups="%s,%s,hr.group_hr_user" % (COMPENSATION, CFO),
        help="The total monthly basic increase the cycle may approve.",
    )
    guideline_pct = fields.Float(
        string="Guideline Increase %", help="The increase a manager is expected to stay within."
    )
    guidelines = fields.Text()
    state = fields.Selection(
        [("draft", "Draft"), ("open", "Open"), ("closed", "Closed")],
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )
    proposal_ids = fields.One2many("fix.compensation.proposal", "cycle_id", string="Proposals")
    committed_amount = fields.Monetary(
        string="Approved Increases",
        currency_field="currency_id",
        compute="_compute_spend",
        compute_sudo=True,
        groups="%s,%s,hr.group_hr_user" % (COMPENSATION, CFO),
    )
    pending_amount = fields.Monetary(
        string="Increases Awaiting Decision",
        currency_field="currency_id",
        compute="_compute_spend",
        compute_sudo=True,
        groups="%s,%s,hr.group_hr_user" % (COMPENSATION, CFO),
    )
    remaining_amount = fields.Monetary(
        string="Budget Remaining",
        currency_field="currency_id",
        compute="_compute_spend",
        compute_sudo=True,
        groups="%s,%s,hr.group_hr_user" % (COMPENSATION, CFO),
    )
    opened_by_id = fields.Many2one("res.users", string="Opened By", readonly=True)
    opened_at = fields.Datetime(string="Opened At", readonly=True)
    closed_by_id = fields.Many2one("res.users", string="Closed By", readonly=True)
    closed_at = fields.Datetime(string="Closed At", readonly=True)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    _TERMS = frozenset(
        {"name", "company_id", "date_from", "date_to", "currency_id", "budget", "guideline_pct"}
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "opened_by_id",
            "opened_at",
            "closed_by_id",
            "closed_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(rec.state != "draft" for rec in self):
            locked = locked | self._TERMS
        return locked

    @api.depends("proposal_ids.state", "proposal_ids.proposed_basic", "budget")
    def _compute_spend(self):
        for rec in self:
            props = rec.sudo().proposal_ids

            def increase(rows):
                return sum((p.proposed_basic or 0.0) - (p.current_basic or 0.0) for p in rows)

            rec.committed_amount = increase(props.filtered(lambda p: p.state == "approved"))
            rec.pending_amount = increase(
                props.filtered(lambda p: p.state in ("submitted", "calibrated"))
            )
            rec.remaining_amount = (rec.sudo().budget or 0.0) - rec.committed_amount

    @api.constrains("date_from", "date_to", "guideline_pct")
    def _check_terms(self):
        for rec in self:
            if rec.date_to < rec.date_from:
                raise ValidationError("A compensation cycle ends after it starts.")
            if rec.guideline_pct < 0 or rec.guideline_pct > 100:
                raise ValidationError("The guideline increase is a percentage (0-100).")

    @api.model_create_multi
    def create(self, vals_list):
        require_group(self.env, COMPENSATION, "Setting up a compensation cycle")
        return super().create(vals_list)

    def write(self, vals):
        guard_first(self, vals)
        if not self._fix_guard_open():
            require_group(self.env, COMPENSATION, "Changing a compensation cycle")
            frozen = changed_fields(self.filtered(lambda r: r.state != "draft"), vals, self._TERMS)
            if frozen:
                raise UserError(
                    "An open compensation cycle keeps its window and budget (%s)."
                    % ", ".join(sorted(frozen))
                )
        return super().write(vals)

    def unlink(self):
        if not self.env.su and any(rec.state != "draft" for rec in self):
            raise UserError("Only a draft compensation cycle is deleted.")
        return super().unlink()

    def action_open(self):
        require_group(self.env, COMPENSATION, "Opening a compensation cycle")
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is not a draft." % rec.name)
            if (rec.sudo().budget or 0.0) <= 0:
                raise UserError("BRU-PIC-17: set the cycle's budget before opening it.")
            clash = self.sudo().search(
                [
                    ("id", "!=", rec.id),
                    ("company_id", "=", rec.company_id.id),
                    ("state", "=", "open"),
                    ("date_from", "<=", rec.date_to),
                    ("date_to", ">=", rec.date_from),
                ],
                limit=1,
            )
            if clash:
                raise UserError("%s is already open over those dates." % clash.name)
            rec._guarded().write(
                {
                    "state": "open",
                    "opened_by_id": self.env.user.id,
                    "opened_at": fields.Datetime.now(),
                }
            )
        return True

    def action_close(self):
        require_group(self.env, COMPENSATION, "Closing a compensation cycle")
        for rec in self:
            if rec.state != "open":
                raise UserError("%s is not open." % rec.name)
            waiting = rec.sudo().proposal_ids.filtered(
                lambda p: p.state in ("submitted", "calibrated")
            )
            if waiting:
                raise UserError(
                    "%s still has %d proposal(s) awaiting a decision." % (rec.name, len(waiting))
                )
            rec._guarded().write(
                {
                    "state": "closed",
                    "closed_by_id": self.env.user.id,
                    "closed_at": fields.Datetime.now(),
                }
            )
        return True

    @api.model
    def _fix_cycle_for(self, company, day):
        return self.sudo().search(
            [
                ("company_id", "=", company.id),
                ("state", "=", "open"),
                ("date_from", "<=", day),
                ("date_to", ">=", day),
            ],
            limit=1,
        )


class FixCompensationProposalCycle(models.Model):
    _inherit = "fix.compensation.proposal"

    cycle_id = fields.Many2one(
        "fix.compensation.cycle", string="Compensation Cycle", readonly=True, index=True
    )
    over_budget = fields.Boolean(
        string="Over the Cycle Budget", compute="_compute_over_budget", compute_sudo=True
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"cycle_id"}

    def _fix_cycle_overrun(self):
        """By how much approving this proposal would take its cycle over budget."""
        self.ensure_one()
        rec = self.sudo()
        cycle = rec.cycle_id
        if not cycle:
            return 0.0
        increase = (rec.proposed_basic or 0.0) - (rec.current_basic or 0.0)
        return round(cycle.committed_amount + increase - (cycle.budget or 0.0), 2)

    @api.depends("cycle_id", "proposed_basic", "state")
    def _compute_over_budget(self):
        for rec in self:
            rec.over_budget = (
                rec.state in ("submitted", "calibrated") and rec._fix_cycle_overrun() > 0
            )

    def _approval_group_xmlid(self):
        # BRU-PIC-17: over the cycle budget, the CFO decides.
        if len(self) == 1 and self._fix_cycle_overrun() > 0:
            return CFO
        return super()._approval_group_xmlid()

    @api.model
    def _fix_propose(self, employee, proposed_basic, justification, **kwargs):
        rec = super()._fix_propose(employee, proposed_basic, justification, **kwargs)
        pinned = rec.sudo()
        cycle = self.env["fix.compensation.cycle"]._fix_cycle_for(
            pinned.company_id, pinned.effective_date
        )
        if cycle:
            pinned._guarded().write({"cycle_id": cycle.id})
        return rec

    def action_approve(self):
        for rec in self:
            overrun = rec._fix_cycle_overrun()
            if overrun > 0 and not self.env.su:
                decider = rec._people_decider()
                if not decider.has_group(CFO):
                    raise UserError(
                        "BRU-PIC-17: %s takes %s over its budget by %.2f; the CFO decides it. "
                        "Reject it so the manager can propose again, or ask the CFO."
                        % (rec.name, rec.sudo().cycle_id.name, overrun)
                    )
        return super().action_approve()
