# fix_performance — M57: scorecard, incentives, compensation (P08-M04).
#
# A09 workflow audit (M57-F1/F2/F5/F6/F9/F10): the incentive money path had no
# approval, no segregation of duties and no lock. One user computed a run and
# applied it to payroll; line amounts were edited before and after; the run
# state was written straight to 'applied'; a second run for the period
# overwrote the payslip; and M57 wrote fix.payslip itself (BRU-PIC-09). The
# scorecard KPIs were typed, so the incentive was self-reportable.
#
# Now (interface I4 of the A09 build brief):
#   * scorecards are computed from service-order facts and published; the KPI
#     fields are guarded, nobody types them;
#   * a run is draft -> computed -> approved; approval is routed through the
#     M63 engine (fix.people.approval.mixin) to the Incentive Approver, never
#     the preparer, the computing user or anyone with a line on the run;
#   * lines are created only by the computation and are frozen (guarded);
#   * one run per period and company;
#   * M57 never touches the payslip: payroll (M56) picks up the lines of an
#     approved run and calls fix.incentive.line._fix_attach_payslip(slip).
import calendar
import re
from datetime import date, timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

# Composite score weights (governed): positive weights sum to 1.00 (RAP-M57-01 / RAP-M57-02)
WEIGHTS = {
    "first_time_fix": 0.40,
    "sla_hit": 0.25,
    "csat": 0.20,
    "salvage": 0.15,
    "rework_penalty": 0.15,
    "rework_30d_penalty_max": 0.30,
    "rework_30d_threshold": 0.03,
}

OFFICER = "cd_performance.group_performance_officer"
APPROVER = "cd_performance.group_incentive_approver"
CALIBRATOR = "cd_performance.group_performance_calibrator"
COMPENSATION = "cd_performance.group_compensation"
HR_MANAGER = "hr.group_hr_manager"

PERIOD_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
# BRU-PIC-07: no calculation before the M55 attendance lock. A company may
# switch it off with this parameter ("0") while M55 locks are not in use.
ATTENDANCE_LOCK_PARAM = "cd_performance.incentive_requires_attendance_lock"


def rework_clawback_penalty(rework_30d_rate: float) -> float:
    """RAP-M57-02: >3% 30-day rework penalty ramp (0% at <=3%, -0.30 at 6%).

    The ramp is capped at `rework_30d_penalty_max`: the constant names the
    maximum clawback, so a 12% rework rate must not produce a 0.90 penalty
    four times the governed ceiling. Rates at or below 6% are unaffected.
    """
    if rework_30d_rate < 0 or rework_30d_rate > 1:
        raise ValueError("rework_30d_rate must be 0..1")
    threshold = WEIGHTS["rework_30d_threshold"]
    if rework_30d_rate <= threshold:
        return 0.0
    ramp = (rework_30d_rate - threshold) / threshold
    penalty_max = WEIGHTS["rework_30d_penalty_max"]
    return round(min(penalty_max * ramp, penalty_max), 4)


def composite_score(
    ftf: float,
    sla: float,
    csat: float,
    rework: float = 0.0,
    salvage: float | None = None,
    rework_30d: float | None = None,
) -> float:
    """The explainable composite: weighted positives summing to 1.00 minus rework
    penalty. All inputs 0..1; result clamped 0..1 so top band (>=0.90) is reachable."""
    base_inputs = [ftf, sla, csat, rework]
    if salvage is not None:
        base_inputs.append(salvage)
    if rework_30d is not None:
        base_inputs.append(rework_30d)
    if not all(0 <= v <= 1 for v in base_inputs):
        raise ValueError("scorecard inputs must be 0..1")

    if salvage is None:
        pos_weight_sum = WEIGHTS["first_time_fix"] + WEIGHTS["sla_hit"] + WEIGHTS["csat"]
        positives = (
            WEIGHTS["first_time_fix"] * ftf + WEIGHTS["sla_hit"] * sla + WEIGHTS["csat"] * csat
        ) / pos_weight_sum
    else:
        positives = (
            WEIGHTS["first_time_fix"] * ftf
            + WEIGHTS["sla_hit"] * sla
            + WEIGHTS["csat"] * csat
            + WEIGHTS["salvage"] * salvage
        )

    penalty = WEIGHTS["rework_penalty"] * rework
    if rework_30d is not None:
        penalty += rework_clawback_penalty(rework_30d)

    raw = positives - penalty
    return round(max(0.0, min(1.0, raw)), 4)


def incentive_amount(score: float, band_base: float) -> float:
    """Banded incentive: >=0.90 pays 15% of band base, >=0.75 pays 8%,
    >=0.60 pays 4%, below pays 0. Round to 2dp (it pays people)."""
    if not (0 <= score <= 1) or band_base < 0:
        raise ValueError("score 0..1 and non-negative base required")
    if score >= 0.90:
        rate = 0.15
    elif score >= 0.75:
        rate = 0.08
    elif score >= 0.60:
        rate = 0.04
    else:
        rate = 0.0
    return round(band_base * rate, 2)


def period_bounds(period):
    """(first day, last day) of a 'YYYY-MM' period; UserError otherwise."""
    if not period or not PERIOD_RE.match(period):
        raise UserError("The period must be a month written YYYY-MM (got %r)." % (period or ""))
    year, month = int(period[:4]), int(period[5:7])
    return date(year, month, 1), date(year, month, calendar.monthrange(year, month)[1])


def guard_first(records, vals):
    """Refuse a guarded-field change BEFORE a model's own write checks, so the
    caller is told the field is workflow-owned (the guard's message), not a
    secondary reason."""
    if records and not records._fix_guard_open():
        touched = records._fix_guarded_fields() & set(vals)
        changed = {
            name
            for rec in records
            for name in touched
            if rec._fix_guard_differs(name, vals[name], rec[name])
        }
        if changed:
            records._fix_guard_refuse(changed)


def changed_fields(records, vals, names):
    """The names in `names` that `vals` would really change on any record (the
    P03 form posts every field it shows, so an unchanged value is no change)."""
    return {
        name
        for rec in records
        for name in set(names) & set(vals)
        if rec._fix_guard_differs(name, vals[name], rec[name])
    }


def require_group(env, xmlid, what):
    if env.su or env.user.has_group(xmlid):
        return
    group = env.ref(xmlid, raise_if_not_found=False)
    raise AccessError("%s needs the %s role." % (what, group.name if group else xmlid))


class FixPerformanceScorecard(models.Model):
    _name = "fix.performance.scorecard"
    _description = "Technician Scorecard"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "period desc, employee_id"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    period = fields.Char(required=True, help="YYYY-MM")
    first_time_fix = fields.Float(string="First-Time Fix (0-1)", readonly=True)
    sla_hit = fields.Float(string="SLA Hit Rate (0-1)", readonly=True)
    csat = fields.Float(string="CSAT (normalised 0-1)", readonly=True)
    rework_rate = fields.Float(string="Rework Rate (0-1)", readonly=True)
    rework_30d_rate = fields.Float(
        string="30-Day Rework Rate (0-1)",
        default=0.0,
        readonly=True,
        help="RAP-M57-02: >3% triggers clawback penalty ramp",
    )
    salvage_value = fields.Float(
        string="Component Salvage Value (BDT)",
        default=0.0,
        readonly=True,
        help="Value of recovered/repaired sub-assemblies. No service-order fact "
        "records it yet, so the computation leaves it at 0.",
    )
    salvage_target = fields.Float(
        string="Component Salvage Target (BDT)",
        default=0.0,
        help="Monthly target for salvage recovery; 0 uses 3-factor normalisation",
    )
    salvage_ratio = fields.Float(
        string="Salvage Achievement (0-1)", compute="_compute_score", store=True
    )
    rework_penalty_applied = fields.Float(
        string="Rework Clawback Penalty", compute="_compute_score", store=True
    )
    score = fields.Float(string="Composite Score", compute="_compute_score", store=True)
    state = fields.Selection(
        [("draft", "Draft"), ("published", "Published")],
        default="draft",
        required=True,
        tracking=True,
    )
    facts_orders = fields.Integer(string="Service Orders Counted", readonly=True)
    facts_basis = fields.Char(string="Computation Basis", readonly=True)
    computed_by_id = fields.Many2one("res.users", string="Computed By", readonly=True)
    computed_at = fields.Datetime(string="Computed At", readonly=True)
    published_by_id = fields.Many2one("res.users", string="Published By", readonly=True)
    published_at = fields.Datetime(string="Published At", readonly=True)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    _one_per_period = models.Constraint(
        "UNIQUE (company_id, employee_id, period)",
        "One scorecard per employee and period",
    )

    _KPI_FIELDS = frozenset(
        {"first_time_fix", "sla_hit", "csat", "rework_rate", "rework_30d_rate", "salvage_value"}
    )
    _FROZEN_WHEN_PUBLISHED = frozenset(
        {"employee_id", "period", "company_id", "salvage_target", "operating_unit_id"}
    )

    def _fix_guarded_fields(self) -> set:
        # BRU-PIC-03: the KPIs come from operational facts, never typed.
        return (
            super()._fix_guarded_fields()
            | self._KPI_FIELDS
            | {
                "state",
                "facts_orders",
                "facts_basis",
                "computed_by_id",
                "computed_at",
                "published_by_id",
                "published_at",
            }
        )

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(rec.state == "published" for rec in self):
            locked = locked | self._FROZEN_WHEN_PUBLISHED
        return locked

    @api.depends(
        "first_time_fix",
        "sla_hit",
        "csat",
        "rework_rate",
        "rework_30d_rate",
        "salvage_value",
        "salvage_target",
    )
    def _compute_score(self):
        for rec in self:
            salvage_norm = None
            if rec.salvage_target and rec.salvage_target > 0:
                salvage_norm = max(0.0, min(1.0, (rec.salvage_value or 0.0) / rec.salvage_target))
                rec.salvage_ratio = round(salvage_norm, 4)
            else:
                rec.salvage_ratio = 0.0
            r30 = rec.rework_30d_rate if (rec.rework_30d_rate and rec.rework_30d_rate > 0) else None
            rec.rework_penalty_applied = round(
                WEIGHTS["rework_penalty"] * (rec.rework_rate or 0.0)
                + (rework_clawback_penalty(r30) if r30 is not None else 0.0),
                4,
            )
            rec.score = composite_score(
                rec.first_time_fix or 0.0,
                rec.sla_hit or 0.0,
                rec.csat or 0.0,
                rec.rework_rate or 0.0,
                salvage=salvage_norm,
                rework_30d=r30,
            )

    @api.constrains("period")
    def _check_period(self):
        for rec in self:
            if not PERIOD_RE.match(rec.period or ""):
                raise ValidationError("A scorecard period is a month written YYYY-MM.")

    def write(self, vals):
        guard_first(self, vals)
        if not self._fix_guard_open():
            frozen = changed_fields(
                self.filtered(lambda r: r.state == "published"), vals, self._FROZEN_WHEN_PUBLISHED
            )
            if frozen:
                raise UserError(
                    "A published scorecard keeps what it was published with (%s)."
                    % ", ".join(sorted(frozen))
                )
        return super().write(vals)

    # ---- the facts ----------------------------------------------------------
    def _fix_assert_not_about_self(self, what):
        for rec in self:
            if not self.env.su and rec.employee_id.user_id == self.env.user:
                raise UserError("You cannot %s your own scorecard." % what)

    def _fix_service_order_facts(self):
        """FTF, SLA, CSAT and rework for this employee and month, from the
        service orders they completed (M01) and, when M34 is installed, the
        customers' survey ratings. Returns (values, orders counted, basis)."""
        self.ensure_one()
        start, end = period_bounds(self.period)
        lo = fields.Datetime.to_datetime(start)
        hi = fields.Datetime.to_datetime(end + timedelta(days=1))
        SO = self.env["fix.service.order"].sudo()
        orders = SO.search(
            [
                ("technician_id", "=", self.employee_id.id),
                ("company_id", "=", self.company_id.id),
                ("state", "in", ("delivered", "closed")),
                "|",
                "&",
                ("delivered_at", ">=", lo),
                ("delivered_at", "<", hi),
                "&",
                ("delivered_at", "=", False),
                "&",
                ("closed_at", ">=", lo),
                ("closed_at", "<", hi),
            ]
        )
        n = len(orders)
        basis = ["%d completed service order(s) in %s" % (n, self.period)]
        if not n:
            zero = dict.fromkeys(self._KPI_FIELDS, 0.0)
            return zero, 0, "; ".join([*basis, "no facts: every KPI is 0"])

        reworks = SO.search([("rework_of_id", "in", orders.ids)])
        reworked = set(reworks.mapped("rework_of_id").ids)
        reworked_30d = set()
        for rw in reworks:
            orig = rw.rework_of_id
            done = orig.delivered_at or orig.closed_at
            if done and rw.create_date and rw.create_date <= done + timedelta(days=30):
                reworked_30d.add(orig.id)

        work_counts = {}
        if "fix.work.order" in self.env:
            for row in (
                self.env["fix.work.order"]
                .sudo()
                ._read_group([("order_id", "in", orders.ids)], ["order_id"], ["__count"])
            ):
                work_counts[row[0].id] = row[1]
        first_time = [o for o in orders if o.id not in reworked and work_counts.get(o.id, 0) <= 1]

        with_deadline = orders.filtered(lambda o: o.sla_resolution_deadline)
        hits = with_deadline.filtered(
            lambda o: (
                (o.sla_resolution_at or o.delivered_at or o.closed_at)
                and (o.sla_resolution_at or o.delivered_at or o.closed_at)
                <= o.sla_resolution_deadline
            )
        )
        sla = len(hits) / len(with_deadline) if with_deadline else 0.0
        basis.append("SLA over %d order(s) with a deadline" % len(with_deadline))

        csat = 0.0
        if "fix.survey" in self.env:
            surveys = (
                self.env["fix.survey"]
                .sudo()
                .search([("service_order_id", "in", orders.ids), ("rating", "!=", False)])
            )
            if surveys:
                csat = sum((int(s.rating) - 1) / 4.0 for s in surveys) / len(surveys)
            basis.append("CSAT from %d survey rating(s)" % len(surveys))
        else:
            basis.append("CSAT 0: the M34 survey module is not installed")
        basis.append("salvage 0: no fact source")
        values = {
            "first_time_fix": round(len(first_time) / n, 4),
            "sla_hit": round(sla, 4),
            "csat": round(max(0.0, min(1.0, csat)), 4),
            "rework_rate": round(len(reworked) / n, 4),
            "rework_30d_rate": round(len(reworked_30d) / n, 4),
            "salvage_value": 0.0,
        }
        return values, n, "; ".join(basis)

    def action_compute_from_orders(self):
        """Recompute the KPIs from the facts (draft scorecards only)."""
        require_group(self.env, OFFICER, "Computing a scorecard")
        self._fix_assert_not_about_self("compute")
        for rec in self:
            if rec.state != "draft":
                raise UserError("A published scorecard is final; it is not recomputed.")
            values, n, basis = rec._fix_service_order_facts()
            rec._guarded().write(
                {
                    **values,
                    "facts_orders": n,
                    "facts_basis": basis,
                    "computed_by_id": self.env.user.id,
                    "computed_at": fields.Datetime.now(),
                }
            )
        return True

    def action_publish(self):
        require_group(self.env, OFFICER, "Publishing a scorecard")
        self._fix_assert_not_about_self("publish")
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is already published." % rec.display_name)
            if not rec.computed_at and not self.env.su:
                raise UserError(
                    "Compute the scorecard from the service orders before publishing it."
                )
            rec._guarded().write(
                {
                    "state": "published",
                    "published_by_id": self.env.user.id,
                    "published_at": fields.Datetime.now(),
                }
            )
            publish(
                self.env,
                "scorecard.published",
                "fix.performance.scorecard",
                rec.id,
                {"employee": rec.employee_id.name, "period": rec.period, "score": rec.score},
            )
        return True


class FixIncentiveRun(models.Model):
    _name = "fix.incentive.run"
    _description = "Incentive Run"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.people.approval.mixin"]
    _order = "period desc"
    _rec_name = "period"

    _approval_domain = "hr_incentive"
    _approval_apply_method = "action_approve"
    _approval_group = APPROVER

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    period = fields.Char(required=True, help="YYYY-MM")
    band_base = fields.Monetary(
        string="Band Base",
        currency_field="currency_id",
        required=True,
        groups="%s,%s" % (OFFICER, APPROVER),
        help="T5-protected compensation input (05-04 4-5): the incentive officer "
        "who prepares the run and the approver who decides it read it.",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    state = fields.Selection(
        [("draft", "Draft"), ("computed", "Computed"), ("approved", "Approved")],
        default="draft",
        required=True,
        tracking=True,
    )
    line_ids = fields.One2many("fix.incentive.line", "run_id", string="Incentive Lines")
    total = fields.Monetary(compute="_compute_total", currency_field="currency_id", string="Total")
    computed_by_id = fields.Many2one("res.users", string="Computed By", readonly=True)
    computed_at = fields.Datetime(string="Computed At", readonly=True)
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True)
    approved_at = fields.Datetime(string="Approved At", readonly=True)
    approved_total = fields.Monetary(
        string="Approved Total", currency_field="currency_id", readonly=True
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    _one_run_per_period = models.Constraint(
        "UNIQUE (company_id, period)", "One incentive run per period and company"
    )

    _FROZEN_AFTER_DRAFT = frozenset(
        {"period", "band_base", "company_id", "currency_id", "operating_unit_id"}
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "computed_by_id",
            "computed_at",
            "approved_by_id",
            "approved_at",
            "approved_total",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(rec.state != "draft" for rec in self):
            locked = locked | self._FROZEN_AFTER_DRAFT
        return locked

    @api.depends("line_ids.amount")
    def _compute_total(self):
        for rec in self:
            rec.total = sum(rec.line_ids.mapped("amount"))

    @api.constrains("period")
    def _check_period(self):
        for rec in self:
            if not PERIOD_RE.match(rec.period or ""):
                raise ValidationError("An incentive run's period is a month written YYYY-MM.")

    # ---- approval declarations ---------------------------------------------
    def _approval_amount(self) -> float:
        return float(self.total or 0.0)

    def _approval_subject_employees(self):
        # Nobody with a line on the run decides it.
        return self.mapped("line_ids.employee_id")

    def _approval_preparers(self):
        return self.mapped("computed_by_id") | self.mapped("create_uid")

    # ---- writes -------------------------------------------------------------
    def write(self, vals):
        guard_first(self, vals)
        if not self._fix_guard_open():
            frozen = changed_fields(
                self.filtered(lambda r: r.state != "draft"), vals, self._FROZEN_AFTER_DRAFT
            )
            if frozen:
                raise UserError(
                    "A computed or approved incentive run keeps its period and band base "
                    "(%s). Reset a computed run to draft to change them."
                    % ", ".join(sorted(frozen))
                )
        return super().write(vals)

    def unlink(self):
        if not self.env.su and any(rec.state != "draft" for rec in self):
            raise UserError("Only a draft incentive run can be deleted.")
        return super().unlink()

    # ---- transitions ----------------------------------------------------------
    def _fix_attendance_lock_required(self):
        value = self.env["ir.config_parameter"].sudo().get_param(ATTENDANCE_LOCK_PARAM, "1")
        return str(value).strip().lower() not in ("0", "false", "no", "")

    def _fix_assert_attendance_locked(self):
        """BRU-PIC-07: the period's M55 attendance must be locked first."""
        self.ensure_one()
        if not self._fix_attendance_lock_required() or "fix.attendance.lock" not in self.env:
            return
        start, end = period_bounds(self.period)
        lock = (
            self.env["fix.attendance.lock"]
            .sudo()
            .search(
                [
                    ("company_id", "in", (self.company_id.id, False)),
                    ("state", "=", "locked"),
                    ("period_start", "<=", start),
                    ("period_end", ">=", end),
                ],
                limit=1,
            )
        )
        if not lock:
            raise UserError(
                "BRU-PIC-07: lock the %s attendance (M55) before computing incentives for it."
                % self.period
            )

    def action_compute(self):
        """One line per PUBLISHED scorecard of the period; the banded amount."""
        require_group(self.env, OFFICER, "Computing an incentive run")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Compute runs from draft only")
            period_bounds(rec.period)
            base = rec.sudo().band_base or 0.0
            if base <= 0:
                raise UserError("Set a positive band base before computing.")
            rec._fix_assert_attendance_locked()
            scorecards = self.env["fix.performance.scorecard"].search(
                [
                    ("period", "=", rec.period),
                    ("company_id", "=", rec.company_id.id),
                    ("state", "=", "published"),
                ]
            )
            if not scorecards:
                raise UserError("No published scorecards for %s" % rec.period)
            Line = self.env["fix.incentive.line"]._guarded()
            Line.create(
                [
                    {
                        "run_id": rec.id,
                        "company_id": rec.company_id.id,
                        "scorecard_id": sc.id,
                        "employee_id": sc.employee_id.id,
                        "amount": incentive_amount(sc.score, base),
                        "currency_id": rec.currency_id.id,
                    }
                    for sc in scorecards
                ]
            )
            rec._guarded().write(
                {
                    "state": "computed",
                    "computed_by_id": self.env.user.id,
                    "computed_at": fields.Datetime.now(),
                }
            )
        return True

    def action_reset_draft(self):
        """Throw a computed (unapproved) run's lines away and start again."""
        require_group(self.env, OFFICER, "Resetting an incentive run")
        for rec in self:
            if rec.state != "computed":
                raise UserError("Only a computed, unapproved run can be reset to draft.")
            if rec.approval_state == "pending":
                rec._approval_void("the run was reset to draft")
            rec.line_ids._guarded().unlink()
            rec._guarded().write(
                {
                    "state": "draft",
                    "computed_by_id": False,
                    "computed_at": False,
                    "approval_state": "none",
                }
            )
        return True

    def action_request_approval(self, justification=None):
        for rec in self:
            if rec.state != "computed" or not rec.line_ids:
                raise UserError("Compute the run before requesting its approval.")
        return super().action_request_approval(justification=justification)

    def action_approve(self):
        """Run by the approval engine from the approver's inbox task."""
        self._approval_assert_routed()
        self._people_assert_not_conflicted()
        for rec in self:
            if rec.state != "computed":
                raise UserError("Only a computed incentive run can be approved.")
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": rec._people_decider().id,
                    "approved_at": fields.Datetime.now(),
                    "approved_total": rec.total,
                }
            )
            for line in rec.line_ids:
                # Payroll (M56) picks up the approved lines; M57 initiates no
                # payment (BRU-PIC-09).
                publish(
                    self.env,
                    "incentive.granted",
                    "fix.incentive.line",
                    line.id,
                    {
                        "employee": line.employee_id.name,
                        "period": rec.period,
                        "amount": line.amount,
                    },
                )
                publish(
                    self.env,
                    "incentive.approved",
                    "fix.incentive.line",
                    line.id,
                    {
                        "employee_id": line.employee_id.id,
                        "employee": line.employee_id.name,
                        "period": rec.period,
                        "amount": line.amount,
                        "payslip_id": 0,
                    },
                )
        return True


class FixIncentiveLine(models.Model):
    _name = "fix.incentive.line"
    _description = "Incentive Line"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    run_id = fields.Many2one("fix.incentive.run", required=True, ondelete="cascade")
    scorecard_id = fields.Many2one("fix.performance.scorecard", required=True)
    employee_id = fields.Many2one("hr.employee", required=True)
    amount = fields.Monetary(string="Amount", currency_field="currency_id", readonly=True)
    payslip_ref_id = fields.Integer(string="Applied Payslip ID", readonly=True)
    applied_to_payslip = fields.Boolean(string="Applied to Payslip", default=False, readonly=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    run_state = fields.Selection(related="run_id.state", string="Run State")
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    def _fix_guarded_fields(self) -> set:
        # A line is what the computation produced; nobody types one.
        return super()._fix_guarded_fields() | {
            "run_id",
            "scorecard_id",
            "employee_id",
            "amount",
            "currency_id",
            "company_id",
            "payslip_ref_id",
            "applied_to_payslip",
        }

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            raise UserError(
                "Incentive lines are produced by computing the run; they cannot be created by hand."
            )
        return super().create(vals_list)

    def unlink(self):
        if not self._fix_guard_open():
            raise UserError("Incentive lines go only when their draft run is reset.")
        return super().unlink()

    def _fix_attach_payslip(self, slip):
        """I4: payroll (M56) records that these approved lines are paid on `slip`.

        Refused unless the run is approved, the line is the slip's employee and
        period, and the line is not already on another payslip that still
        exists. Idempotent for the same slip."""
        slip.ensure_one()
        if slip._name != "fix.payslip":
            raise UserError("An incentive line is attached to a payslip only.")
        slip_su = slip.sudo()
        period = slip_su.period_id
        ym = period.period_start.strftime("%Y-%m") if period and period.period_start else ""
        for line in self.sudo():
            run = line.run_id
            if run.state != "approved":
                raise UserError(
                    "Incentive run %s is not approved; payroll pays approved lines only."
                    % run.display_name
                )
            if line.employee_id != slip_su.employee_id:
                raise UserError(
                    "Incentive line for %s cannot go on %s's payslip."
                    % (line.employee_id.name, slip_su.employee_id.name)
                )
            if run.period not in (period.name, ym):
                raise UserError(
                    "Incentive run %s is not for payroll period %s." % (run.period, period.name)
                )
            if line.company_id != slip_su.company_id:
                raise UserError("The incentive line and the payslip belong to other companies.")
            if (
                line.payslip_ref_id
                and line.payslip_ref_id != slip.id
                and self.env["fix.payslip"].sudo().browse(line.payslip_ref_id).exists()
            ):
                raise UserError(
                    "Incentive line %s is already paid on payslip %s."
                    % (line.id, line.payslip_ref_id)
                )
        self.sudo()._guarded().write({"payslip_ref_id": slip.id, "applied_to_payslip": True})
        return True


class FixCompensationBand(models.Model):
    """Compensation banding — T5-tier data throughout (P08-M04-T06)."""

    _name = "fix.compensation.band"
    _description = "Compensation Band"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    name = fields.Char(required=True)
    grade = fields.Char(required=True)
    range_min = fields.Monetary(
        string="Range Min", currency_field="currency_id", groups=COMPENSATION
    )
    range_mid = fields.Monetary(
        string="Range Mid", currency_field="currency_id", groups=COMPENSATION
    )
    range_max = fields.Monetary(
        string="Range Max", currency_field="currency_id", groups=COMPENSATION
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    @api.constrains("range_min", "range_mid", "range_max")
    def _check_range(self):
        for rec in self.sudo():
            if not (rec.range_min <= rec.range_mid <= rec.range_max):
                raise UserError("Band range must be min <= mid <= max")
            if rec.range_min < 0:
                raise UserError("A band range cannot be negative.")

    @api.constrains("grade", "company_id")
    def _check_one_band_per_grade(self):
        for rec in self:
            twins = self.sudo().search_count(
                [
                    ("id", "!=", rec.id),
                    ("grade", "=", rec.grade),
                    ("company_id", "=", rec.company_id.id),
                ]
            )
            if twins:
                raise ValidationError(
                    "Grade %s already has a compensation band in %s."
                    % (rec.grade, rec.company_id.name)
                )

    # ---- I7: the band check other modules call ---------------------------
    @api.model
    def _fix_band_for(self, grade, company=None):
        """The configured band (ranges set) for a grade, or an empty recordset."""
        if not grade:
            return self.browse()
        company = company or self.env.company
        return self.sudo().search(
            [
                ("grade", "=", grade),
                ("company_id", "in", (company.id, False)),
                ("range_max", ">", 0),
            ],
            order="company_id desc",
            limit=1,
        )

    @api.model
    def _fix_check_amount(self, grade, amount, company=None, what="The salary"):
        """I7: refuse `amount` outside the grade's band. No configured band
        (none, or its ranges empty) means no check: the band is the rule."""
        band = self._fix_band_for(grade, company)
        if not band:
            return True
        lo, hi = band.range_min, band.range_max
        if not (lo <= (amount or 0.0) <= hi):
            raise ValidationError(
                "%s of %.2f is outside the %s band for grade %s (%.2f to %.2f). "
                "A salary outside the band needs the band changed by the "
                "Compensation Manager first." % (what, amount or 0.0, band.name, grade, lo, hi)
            )
        return True
