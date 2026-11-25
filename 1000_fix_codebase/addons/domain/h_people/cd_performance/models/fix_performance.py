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

# M01 owns the Asia/Dhaka business-day conversion (M57-F6): reuse it, never
# reimplement it. The month boundary of a scorecard is the Dhaka business day,
# not UTC midnight.
from odoo.addons.cd_service_order.models.fix_service_order import _dhaka_date
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
# BRU-PIC-12: days an employee has to dispute a computed line (0 = no window).
DISPUTE_DAYS_PARAM = "cd_performance.incentive_dispute_days"
# BRU-PIC-11: a rework or credit within this many days of the order's
# completion claws its share of the paid incentive back (0 = no clawback).
CLAWBACK_DAYS_PARAM = "cd_performance.incentive_clawback_days"
# M57-F4: the smallest share of the composite's configured weight that must
# have a fact source before a scorecard may be published (0.0 = no gate; the
# composite still renormalises over the components that have data). The figure
# is an OWNER decision (recommend 0.6).
MIN_FACT_COVERAGE_PARAM = "cd_performance.min_fact_coverage"


def float_param(env, key, default=0.0):
    """A setting held as a decimal share (0..1); anything unreadable is the
    default."""
    raw = env["ir.config_parameter"].sudo().get_param(key, str(default))
    try:
        return round(max(float(str(raw).strip() or 0.0), 0.0), 4)
    except (TypeError, ValueError):
        return default


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
    ftf: float | None,
    sla: float | None,
    csat: float | None,
    rework: float = 0.0,
    salvage: float | None = None,
    rework_30d: float | None = None,
) -> float:
    """The explainable composite: weighted positives summing to 1.00 minus rework
    penalty. All inputs 0..1; result clamped 0..1 so top band (>=0.90) is reachable.

    M57-F4/F7: a positive component whose value is None has no fact source —
    it is EXCLUDED and the composite renormalises over the weighted components
    that have data, so missing data is never scored as the worst score. With
    every component missing there is nothing to score: 0.0."""
    inputs = {"first_time_fix": ftf, "sla_hit": sla, "csat": csat}
    if salvage is not None:
        inputs["salvage"] = salvage
    # a rework rate nobody measured is no rework evidence, not a crash: the
    # validation below skips the components that have no fact source
    rework_value = 0.0 if rework is None else rework
    base_inputs = [*inputs.values(), rework_value]
    if rework_30d is not None:
        base_inputs.append(rework_30d)
    measured = [v for v in base_inputs if v is not None]
    if not all(0 <= v <= 1 for v in measured):
        raise ValueError("scorecard inputs must be 0..1")

    weighted = [(WEIGHTS[k], v) for k, v in inputs.items() if v is not None]
    pos_weight_sum = sum(w for w, _v in weighted)
    if pos_weight_sum <= 0:
        return 0.0
    positives = sum(w * v for w, v in weighted) / pos_weight_sum

    penalty = WEIGHTS["rework_penalty"] * rework_value
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


def int_param(env, key, default=0):
    """A non-negative integer setting; a value that is not a number reads as
    the default."""
    raw = env["ir.config_parameter"].sudo().get_param(key, str(default))
    try:
        return max(int(str(raw).strip() or 0), 0)
    except (TypeError, ValueError):
        return default


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
    # M57-F4/F7: which components the computation found facts for. A component
    # without facts is excluded from the composite (renormalised), not scored 0.
    # Defaults True so a typed seed card behaves as before; the computation
    # from service orders writes the real flags.
    sla_has_facts = fields.Boolean(
        string="SLA Has Data", default=True, help="False: no counted order carries a deadline."
    )
    csat_has_facts = fields.Boolean(
        string="CSAT Has Data", default=True, help="False: no customer survey rating exists."
    )
    salvage_has_facts = fields.Boolean(
        string="Salvage Has Data",
        default=True,
        help="False: no fact source records salvage value yet (the computation "
        "always writes 0 today), so the component is excluded even when a "
        "target is set.",
    )
    facts_coverage = fields.Float(
        string="Fact Coverage (0-1)",
        compute="_compute_score",
        store=True,
        help="The share of the composite's configured weight that has a fact source.",
    )
    insufficient_data = fields.Boolean(
        string="Insufficient Data",
        compute="_compute_score",
        store=True,
        help="True when fact coverage is below the ruled minimum "
        "(cd_performance.min_fact_coverage; 0 = no gate).",
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
    _FACT_FLAG_FIELDS = frozenset({"sla_has_facts", "csat_has_facts", "salvage_has_facts"})
    _FROZEN_WHEN_PUBLISHED = frozenset(
        {"employee_id", "period", "company_id", "salvage_target", "operating_unit_id"}
    )

    def _fix_guarded_fields(self) -> set:
        # BRU-PIC-03: the KPIs come from operational facts, never typed.
        return (
            super()._fix_guarded_fields()
            | self._KPI_FIELDS
            | self._FACT_FLAG_FIELDS
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
        "sla_has_facts",
        "csat_has_facts",
        "salvage_has_facts",
    )
    def _compute_score(self):
        for rec in self:
            salvage_configured = bool(rec.salvage_target and rec.salvage_target > 0)
            salvage_norm = None
            if salvage_configured and rec.salvage_has_facts:
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
                rec.sla_hit if rec.sla_has_facts else None,
                rec.csat if rec.csat_has_facts else None,
                rec.rework_rate or 0.0,
                salvage=salvage_norm,
                rework_30d=r30,
            )
            # M57-F4: coverage = the configured weight that has a fact source.
            configured = WEIGHTS["first_time_fix"] + WEIGHTS["sla_hit"] + WEIGHTS["csat"]
            if salvage_configured:
                configured += WEIGHTS["salvage"]
            covered = (
                WEIGHTS["first_time_fix"]
                + (WEIGHTS["sla_hit"] if rec.sla_has_facts else 0.0)
                + (WEIGHTS["csat"] if rec.csat_has_facts else 0.0)
            )
            if salvage_configured and rec.salvage_has_facts:
                covered += WEIGHTS["salvage"]
            rec.facts_coverage = round(covered / configured, 4) if configured else 0.0
            rec.insufficient_data = rec.facts_coverage < float_param(
                self.env, MIN_FACT_COVERAGE_PARAM
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

    def _fix_counted_orders(self):
        """The service orders this scorecard counts: the employee's orders
        completed (delivered or closed) in the period, attributed to the
        technician the order names at its close. M57-F6: the period bounds are
        the Asia/Dhaka business day (M01's own conversion), not UTC midnight —
        an order delivered at 02:30 Dhaka on the 1st belongs to the new month.
        The SQL window is widened a day each side, then the Dhaka date decides."""
        self.ensure_one()
        start, end = period_bounds(self.period)
        lo = fields.Datetime.to_datetime(start - timedelta(days=1))
        hi = fields.Datetime.to_datetime(end + timedelta(days=2))
        candidates = (
            self.env["fix.service.order"]
            .sudo()
            .search(
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
        )
        return candidates.filtered(
            lambda o: start <= _dhaka_date(o.delivered_at or o.closed_at) <= end
        )

    def _fix_service_order_facts(self):
        """FTF, SLA, CSAT and rework for this employee and month, from the
        service orders they completed (M01) and, when M34 is installed, the
        customers' survey ratings. Returns (values, orders counted, basis).

        M57-F4: a component whose fact source is empty (no order with a
        deadline -> SLA; no survey rating -> CSAT; no salvage fact at all) is
        flagged without facts and excluded from the renormalised composite,
        never scored as zero. M57-F5: a rework order is not a first-time fix
        for whoever does the rework (excluded from the FTF numerator AND
        denominator), and only a rework that reached intake counts as rework
        against the original technician (a draft or cancelled one does not)."""
        self.ensure_one()
        SO = self.env["fix.service.order"].sudo()
        orders = self._fix_counted_orders()
        n = len(orders)
        basis = ["%d completed service order(s) in %s" % (n, self.period)]
        if not n:
            zero = dict.fromkeys(self._KPI_FIELDS, 0.0)
            zero.update(
                {"sla_has_facts": False, "csat_has_facts": False, "salvage_has_facts": False}
            )
            return zero, 0, "; ".join([*basis, "no facts: every KPI is 0"])

        reworks = SO.search(
            [
                ("rework_of_id", "in", orders.ids),
                # M57-F5: a cancelled or draft rework order is no rework yet.
                ("state", "not in", ("draft", "cancelled")),
            ]
        )
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
        # M57-F5: a rework order is excluded from both sides of first-time fix.
        non_rework_orders = [o for o in orders if not (o.rework_of_id or o.is_rework)]
        first_time = [
            o for o in non_rework_orders if o.id not in reworked and work_counts.get(o.id, 0) <= 1
        ]

        with_deadline = orders.filtered(lambda o: o.sla_resolution_deadline)
        hits = with_deadline.filtered(
            lambda o: (
                (o.sla_resolution_at or o.delivered_at or o.closed_at)
                and (o.sla_resolution_at or o.delivered_at or o.closed_at)
                <= o.sla_resolution_deadline
            )
        )
        sla = len(hits) / len(with_deadline) if with_deadline else 0.0
        if with_deadline:
            basis.append("SLA over %d order(s) with a deadline" % len(with_deadline))
        else:
            basis.append("SLA: no order carries a deadline - component excluded")

        csat = 0.0
        csat_has_facts = False
        if "fix.survey" in self.env:
            Survey = self.env["fix.survey"].sudo()
            domain = [("service_order_id", "in", orders.ids), ("rating", "!=", False)]
            # M34 BRU-CXM-11 / AUT-CXM-13: a response under an open or upheld
            # anomaly investigation stays out of the incentive calculation.
            if "incentive_excluded" in Survey._fields:
                held = Survey.search_count([*domain, ("incentive_excluded", "=", True)])
                domain.append(("incentive_excluded", "=", False))
                if held:
                    basis.append("%d survey rating(s) held by an anomaly review" % held)
            surveys = Survey.search(domain)
            if surveys:
                csat = sum((int(s.rating) - 1) / 4.0 for s in surveys) / len(surveys)
                csat_has_facts = True
            basis.append(
                "CSAT from %d survey rating(s)%s"
                % (len(surveys), "" if surveys else " - component excluded")
            )
        else:
            basis.append("CSAT: the M34 survey module is not installed - component excluded")
        basis.append("salvage: no fact source - component excluded")
        ftf_base = len(non_rework_orders) or n
        values = {
            "first_time_fix": round(len(first_time) / ftf_base, 4),
            "sla_hit": round(sla, 4),
            "csat": round(max(0.0, min(1.0, csat)), 4),
            "rework_rate": round(len(reworked) / n, 4),
            "rework_30d_rate": round(len(reworked_30d) / n, 4),
            "salvage_value": 0.0,
            "sla_has_facts": bool(with_deadline),
            "csat_has_facts": csat_has_facts,
            "salvage_has_facts": False,
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
            # M57-F4: a ruled minimum coverage gates publication (0 = no gate).
            minimum = float_param(self.env, MIN_FACT_COVERAGE_PARAM)
            if minimum > 0 and (rec.facts_coverage or 0.0) < minimum:
                raise UserError(
                    "%s covers only %.0f%% of the composite's configured weight with facts "
                    "(the ruled minimum is %.0f%%): it is flagged insufficient data. Gather "
                    "the facts or rule a lower minimum (cd_performance.min_fact_coverage)."
                    % (rec.display_name, (rec.facts_coverage or 0.0) * 100, minimum * 100)
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
    scheme_id = fields.Many2one(
        "fix.incentive.scheme",
        string="Incentive Scheme",
        ondelete="restrict",
        help="Empty: the company's only active scheme.",
    )
    # BRU-PIC-01/02: the approved version the run computed under, pinned.
    scheme_version_id = fields.Many2one(
        "fix.incentive.scheme.version",
        string="Scheme Version Applied",
        readonly=True,
        ondelete="restrict",
    )
    band_base = fields.Monetary(
        string="Band Base",
        currency_field="currency_id",
        readonly=True,
        groups="%s,%s" % (OFFICER, APPROVER),
        help="T5-protected compensation input (05-04 4-5): copied from the approved scheme "
        "version when the run is computed. Read by the incentive officer and the approver.",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("computed", "Computed"),
            ("approved", "Approved"),
            ("void", "Voided (before payment)"),
        ],
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
    # M57-F19: a routed void of an approved run before any line is paid.
    void_pending = fields.Boolean(
        string="Void Requested", readonly=True, copy=False, help="A void awaits its second decider."
    )
    void_requested_by_id = fields.Many2one("res.users", string="Void Requested By", readonly=True)
    voided_by_id = fields.Many2one("res.users", string="Voided By", readonly=True)
    voided_at = fields.Datetime(string="Voided At", readonly=True)
    void_reason = fields.Text(string="Void Reason", readonly=True)
    # M57-F11: the clawbacks this run's computation raised against past runs;
    # they stand on the run's approval statement (the approver approves them
    # with the run).
    raised_clawback_ids = fields.One2many(
        "fix.incentive.clawback", "raised_run_id", string="Clawbacks Raised by This Run"
    )
    dispute_deadline = fields.Date(
        string="Disputes Close On",
        readonly=True,
        help="BRU-PIC-12: employees dispute their line until this day; approval is "
        "requested after it. Empty: no dispute window is ruled.",
    )
    dispute_ids = fields.One2many("fix.incentive.dispute", "run_id", string="Disputes")
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    _one_run_per_period = models.Constraint(
        "UNIQUE (company_id, period)", "One incentive run per period and company"
    )

    _FROZEN_AFTER_DRAFT = frozenset(
        {"period", "scheme_id", "company_id", "currency_id", "operating_unit_id"}
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "scheme_version_id",
            "band_base",
            "computed_by_id",
            "computed_at",
            "approved_by_id",
            "approved_at",
            "approved_total",
            "dispute_deadline",
            "void_pending",
            "void_requested_by_id",
            "voided_by_id",
            "voided_at",
            "void_reason",
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
        preparers = self.mapped("computed_by_id") | self.mapped("create_uid")
        # M57-F19: the void decision is a second person — never the one who
        # requested the void nor the approver of the original computation.
        if any(rec.void_pending for rec in self):
            preparers |= self.mapped("void_requested_by_id") | self.mapped("approved_by_id")
        return preparers

    # ---- writes -------------------------------------------------------------
    def write(self, vals):
        guard_first(self, vals)
        if not self._fix_guard_open():
            frozen = changed_fields(
                self.filtered(lambda r: r.state != "draft"), vals, self._FROZEN_AFTER_DRAFT
            )
            if frozen:
                raise UserError(
                    "A computed or approved incentive run keeps its period and scheme "
                    "(%s). Reset a computed run to draft to change them."
                    % ", ".join(sorted(frozen))
                )
        return super().write(vals)

    def unlink(self):
        if not self.env.su and any(rec.state != "draft" for rec in self):
            raise UserError("Only a draft incentive run can be deleted.")
        return super().unlink()

    # ---- the scheme (BRU-PIC-01/02) ----------------------------------------------
    def _fix_scheme_version(self):
        """The scheme and its APPROVED version in force at the period end."""
        self.ensure_one()
        _start, end = period_bounds(self.period)
        scheme = self.scheme_id or self.env["fix.incentive.scheme"]._fix_scheme_for(self.company_id)
        if not scheme:
            raise UserError(
                "Name the incentive scheme this run computes under (the company does not "
                "have exactly one active scheme)."
            )
        version = scheme._fix_version_for(end)
        if not version:
            raise UserError(
                "BRU-PIC-01/02: %s has no version approved by the HR Director and the CFO "
                "in force on %s. A run computes only under an approved scheme version."
                % (scheme.display_name, end)
            )
        return scheme, version

    # ---- proration and eligibility (FR-PIC-028/032) ----------------------------
    def _fix_proration(self, employee, version, start, end):
        """Days the employee earns in the period: joiners from their joining
        date, leavers to their left date, less approved long leave, and the
        scheme's minimum service. Calendar days.

        M57-F9 (AUT-PIC-12, BRU-PIC-15, FR-PIC-028): while the scheme version
        rules `pip_ineligible` (default True), an employee on an ACTIVE PIP or
        under an OPEN disciplinary case (BLA s.23/24) is not eligible for the
        incentive of the period."""
        emp = employee.sudo()
        period_days = (end - start).days + 1
        join = emp.joining_date if "joining_date" in emp._fields else False
        left = emp.left_date if "left_date" in emp._fields else False

        def out(eligible, days, note):
            return {
                "eligible": eligible,
                "eligible_days": days,
                "period_days": period_days,
                "proration_factor": round(days / period_days, 4) if eligible else 0.0,
                "eligibility_note": note,
            }

        if getattr(version, "pip_ineligible", True):
            pip = self.env["fix.performance.pip"]
            active_pip = pip.sudo().search(
                [
                    ("employee_id", "=", emp.id),
                    ("company_id", "=", self.company_id.id),
                    ("state", "=", "active"),
                ],
                limit=1,
            )
            if active_pip:
                return out(
                    False,
                    0,
                    "not eligible: on an active PIP (%s to %s), and the scheme version "
                    "excludes a PIP from the incentive"
                    % (active_pip.start_date, active_pip.end_date),
                )
            if "fix.hr.disciplinary.case" in self.env:
                Case = self.env["fix.hr.disciplinary.case"]
                open_case = Case.sudo().search(
                    [
                        ("employee_id", "=", emp.id),
                        ("company_id", "=", self.company_id.id),
                        ("state", "not in", ("decided", "cancelled")),
                    ],
                    limit=1,
                )
                if open_case:
                    return out(
                        False,
                        0,
                        "not eligible: under an open disciplinary case (%s, state %s), and "
                        "the scheme version excludes an open case from the incentive"
                        % (open_case.name, open_case.state),
                    )
        if version.min_service_days:
            if not join:
                return out(
                    False,
                    0,
                    "not eligible: no joining date recorded, and the scheme needs %d days "
                    "of service" % version.min_service_days,
                )
            service = (end - join).days + 1
            if service < version.min_service_days:
                return out(
                    False,
                    0,
                    "not eligible: %d days of service on %s, the scheme needs %d"
                    % (max(service, 0), end, version.min_service_days),
                )
        lo = max(start, join) if join else start
        hi = min(end, left) if left else end
        if hi < lo:
            return out(False, 0, "not eligible: not employed in %s" % self.period)
        days = {lo + timedelta(days=i) for i in range((hi - lo).days + 1)}
        notes = []
        if join and join > start:
            notes.append("joined %s" % join)
        if left and left < end:
            notes.append("left %s" % left)
        if version.long_leave_days and "fix.leave.request" in self.env:
            leaves = (
                self.env["fix.leave.request"]
                .sudo()
                .search(
                    [
                        ("employee_id", "=", emp.id),
                        ("state", "=", "approved"),
                        ("date_from", "<=", hi),
                        ("date_to", ">=", lo),
                    ]
                )
            )
            for leave in leaves:
                length = (leave.date_to - leave.date_from).days + 1
                if length < version.long_leave_days:
                    continue
                taken = {leave.date_from + timedelta(days=i) for i in range(length)} & days
                if taken:
                    days -= taken
                    notes.append(
                        "%d day(s) of long leave (%s to %s)"
                        % (len(taken), leave.date_from, leave.date_to)
                    )
        note = "; ".join(notes) or "full period"
        return out(True, len(days), "%d of %d days: %s" % (len(days), period_days, note))

    # ---- clawback (BRU-PIC-11) ---------------------------------------------------
    def _fix_clawback_trigger(self, order, days, since):
        """(kind, reference, when) of the first rework or credit of `order`
        raised within `days` of its completion and after `since` (the
        scorecard computation: a rework already in the score is not clawed
        back twice). None when there is none."""
        done = order.delivered_at or order.closed_at
        if not done:
            return None
        limit = done + timedelta(days=days)
        since = since or done
        rework = (
            self.env["fix.service.order"]
            .sudo()
            .search(
                [
                    ("rework_of_id", "=", order.id),
                    ("create_date", "<=", limit),
                    ("create_date", ">", since),
                ],
                order="create_date asc",
                limit=1,
            )
        )
        if rework:
            return "rework", rework.display_name, rework.create_date
        if "fix.credit.note" in self.env and "fix.ar.invoice" in self.env:
            invoices = (
                self.env["fix.ar.invoice"]
                .sudo()
                .search([("source_model", "=", "fix.service.order"), ("source_id", "=", order.id)])
            )
            if invoices:
                note = (
                    self.env["fix.credit.note"]
                    .sudo()
                    .search(
                        [
                            ("invoice_id", "in", invoices.ids),
                            ("state", "in", ("approved", "issued")),
                            ("create_date", "<=", limit),
                            ("create_date", ">", since),
                        ],
                        order="create_date asc",
                        limit=1,
                    )
                )
                if note:
                    return "credit", note.display_name, note.create_date
        return None

    def _fix_raise_clawbacks(self):
        """Clawbacks for orders paid in earlier APPROVED runs that were
        reworked or credited within the window. Each order of each paid line
        is clawed back once. M57-F11: the employee is notified the moment a
        clawback is raised against them, and the clawback stands on this run's
        approval statement (the approver approves the clawbacks with the run)."""
        self.ensure_one()
        days = self._fix_window_days(CLAWBACK_DAYS_PARAM)
        Clawback = self.env["fix.incentive.clawback"].sudo()._guarded()
        if not days:
            return Clawback.browse()
        start, _end = period_bounds(self.period)
        horizon = start - timedelta(days=days + 62)
        paid = (
            self.env["fix.incentive.line"]
            .sudo()
            .search(
                [
                    ("company_id", "=", self.company_id.id),
                    ("run_id", "!=", self.id),
                    ("run_id.state", "=", "approved"),
                    ("run_id.period", "<", self.period),
                    ("line_type", "=", "incentive"),
                    ("amount", ">", 0),
                ]
            )
            .filtered(lambda line: period_bounds(line.run_id.period)[1] >= horizon)
        )
        created = Clawback.browse()
        for line in paid:
            card = line.scorecard_id.sudo()
            orders = card._fix_counted_orders()
            share = round(line.amount / max(card.facts_orders or len(orders), 1), 2)
            since = card.computed_at or card.published_at
            done = set(
                Clawback.search([("source_line_id", "=", line.id)]).mapped("service_order_id").ids
            )
            for order in orders:
                if order.id in done:
                    continue
                trigger = self._fix_clawback_trigger(order, days, since)
                if not trigger:
                    continue
                kind, ref, when = trigger
                cb = Clawback.create(
                    {
                        "company_id": self.company_id.id,
                        "employee_id": line.employee_id.id,
                        "source_line_id": line.id,
                        "raised_run_id": self.id,
                        "service_order_id": order.id,
                        "trigger": kind,
                        "trigger_ref": ref,
                        "trigger_at": when,
                        "amount": share,
                        "currency_id": line.currency_id.id,
                    }
                )
                created |= cb
                # M57-F11: notice before any deduction, not after the fact.
                note = (
                    "A clawback of %.2f BDT was raised against your %s incentive: %s %s on "
                    "service order %s. It is recovered from a later run's incentive, never "
                    "more than you earn in a run, and it is approved with the %s run."
                    % (
                        cb.amount,
                        line.run_id.period,
                        kind,
                        ref,
                        order.display_name,
                        self.period,
                    )
                )
                cb.message_post(body=note)
                user = line.employee_id.sudo().user_id
                if user and user.active:
                    cb.message_subscribe(partner_ids=user.partner_id.ids)
                    cb.activity_schedule(
                        "mail.mail_activity_data_todo",
                        date_deadline=fields.Date.context_today(self),
                        summary="An incentive clawback was raised: %s" % cb.name,
                        note=note,
                        user_id=user.id,
                    )
        return created

    # ---- transitions ----------------------------------------------------------
    def _fix_window_days(self, param_key):
        """M57-F10: the dispute / clawback window. The scheme version the run
        computed under may rule its own figure (visible and editable on the
        version form, frozen with its terms); 0 on the version falls back to
        the estate parameter (0 = off). The figures are an OWNER decision
        (recommend: dispute 5 days, clawback 30 days)."""
        self.ensure_one()
        version_days = False
        version = self.scheme_version_id
        if not version and self.state == "draft":
            try:
                _scheme, version = self._fix_scheme_version()
            except UserError:
                version = self.env["fix.incentive.scheme.version"]
        field = "dispute_days" if param_key == DISPUTE_DAYS_PARAM else "clawback_days"
        if version and field in version._fields:
            version_days = version.sudo()[field]
        if version_days:
            return max(int(version_days), 0)
        return int_param(self.env, param_key)

    def _fix_recover_clawbacks(self, lines):
        """Recover open clawbacks from this run's incentive lines, never more
        than the employee earns in the run: an incentive is not turned into a
        wage deduction. What is left stays open for the next run. M57-F11: the
        employee is notified when a clawback is deducted from this run."""
        self.ensure_one()
        Clawback = self.env["fix.incentive.clawback"].sudo()
        Line = self.env["fix.incentive.line"]._guarded()
        earned = {}
        card_of = {}
        for line in lines.filtered(lambda r: r.line_type == "incentive" and r.amount > 0):
            earned[line.employee_id.id] = earned.get(line.employee_id.id, 0.0) + line.amount
            card_of[line.employee_id.id] = line.scorecard_id.id
        if not earned:
            return Line.browse()
        recovered = Line.browse()
        for cb in Clawback.search(
            [
                ("company_id", "=", self.company_id.id),
                ("state", "=", "open"),
                ("employee_id", "in", list(earned)),
            ],
            order="id",
        ):
            avail = round(earned[cb.employee_id.id], 2)
            take = round(min(cb.remaining_amount, avail), 2)
            if take <= 0:
                continue
            earned[cb.employee_id.id] = avail - take
            recovered |= Line.create(
                {
                    "run_id": self.id,
                    "company_id": self.company_id.id,
                    "scorecard_id": card_of[cb.employee_id.id],
                    "employee_id": cb.employee_id.id,
                    "line_type": "clawback",
                    "clawback_id": cb.id,
                    "amount": -take,
                    "gross_amount": -take,
                    "proration_factor": 1.0,
                    "eligible": True,
                    "eligibility_note": "clawback (%s %s on %s)"
                    % (cb.trigger, cb.trigger_ref, cb.service_order_id.display_name),
                    "currency_id": self.currency_id.id,
                }
            )
            # M57-F11: the deduction is notified, never a surprise line.
            note = (
                "A clawback of %.2f BDT (%s on service order %s) is deducted from your %s "
                "incentive; %.2f BDT of it remains open."
                % (
                    take,
                    cb.trigger,
                    cb.service_order_id.display_name,
                    self.period,
                    cb.remaining_amount - take,
                )
            )
            cb.message_post(body=note)
            user = cb.employee_id.sudo().user_id
            if user and user.active:
                cb.activity_schedule(
                    "mail.mail_activity_data_todo",
                    date_deadline=fields.Date.context_today(self),
                    summary="Clawback deducted from your %s incentive" % self.period,
                    note=note,
                    user_id=user.id,
                )
        return recovered

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
        """One line per PUBLISHED scorecard of the period, banded by the
        approved scheme version in force, prorated by days; then clawbacks."""
        require_group(self.env, OFFICER, "Computing an incentive run")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Compute runs from draft only")
            start, end = period_bounds(rec.period)
            scheme, version = rec._fix_scheme_version()
            base = version.sudo().band_base or 0.0
            if base <= 0:
                raise UserError("Scheme version %s has no band base." % version.display_name)
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
            vals_list = []
            for sc in scorecards:
                gross = version._fix_amount_for(sc.score)
                pro = rec._fix_proration(sc.employee_id, version, start, end)
                vals_list.append(
                    {
                        "run_id": rec.id,
                        "company_id": rec.company_id.id,
                        "scorecard_id": sc.id,
                        "employee_id": sc.employee_id.id,
                        "line_type": "incentive",
                        "gross_amount": gross,
                        "amount": round(gross * pro["proration_factor"], 2),
                        "currency_id": rec.currency_id.id,
                        **pro,
                    }
                )
            lines = self.env["fix.incentive.line"]._guarded().create(vals_list)
            rec._fix_raise_clawbacks()
            rec._fix_recover_clawbacks(lines)
            window = rec._fix_window_days(DISPUTE_DAYS_PARAM)
            today = fields.Date.context_today(self)
            rec._guarded().write(
                {
                    "state": "computed",
                    "scheme_id": scheme.id,
                    "scheme_version_id": version.id,
                    "band_base": base,
                    "computed_by_id": self.env.user.id,
                    "computed_at": fields.Datetime.now(),
                    "dispute_deadline": today + timedelta(days=window) if window else False,
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
                    "scheme_version_id": False,
                    "band_base": 0.0,
                    "computed_by_id": False,
                    "computed_at": False,
                    "dispute_deadline": False,
                    "approval_state": "none",
                }
            )
        return True

    def _fix_assert_disputes_settled(self, requesting=False):
        """BRU-PIC-12: an open dispute (or an upheld one the run was not
        recomputed for) blocks approval; the request waits for the window."""
        today = fields.Date.context_today(self)
        for rec in self:
            if requesting and rec.dispute_deadline and today <= rec.dispute_deadline:
                raise UserError(
                    "BRU-PIC-12: employees may dispute their %s line until %s; request the "
                    "approval after that." % (rec.period, rec.dispute_deadline)
                )
            lines = rec.sudo().line_ids
            blocking = rec.sudo().dispute_ids.filtered(
                lambda d, lines=lines: (
                    d.state == "open" or (d.state == "upheld" and d.line_id in lines)
                )
            )
            if blocking:
                raise UserError(
                    "%s has %d unsettled dispute(s) (%s): answer them, and recompute the run "
                    "for an upheld one, before it is approved."
                    % (rec.period, len(blocking), ", ".join(blocking.mapped("employee_id.name")))
                )

    def _fix_assert_adjustments_applied(self):
        """M57-F20: an approved adjustment of the period that no line of this
        run carries yet blocks the approval — the run is reset and recomputed
        so the adjustment becomes a visible line, or the adjustment is
        cancelled."""
        for rec in self:
            waiting = (
                self.env["fix.incentive.adjustment"]
                .sudo()
                .search(
                    [
                        ("company_id", "=", rec.company_id.id),
                        ("period", "=", rec.period),
                        ("state", "=", "approved"),
                    ]
                )
            )
            if waiting:
                raise UserError(
                    "%s still has %d approved, unapplied adjustment(s) (%s): reset and "
                    "recompute the run so they become visible lines, or cancel them."
                    % (rec.period, len(waiting), ", ".join(waiting.mapped("name")))
                )

    def _fix_clawback_statement(self):
        """M57-F11: the clawbacks the approver approves WITH this run."""
        self.ensure_one()
        raised = self.sudo().raised_clawback_ids
        recovered = self.sudo().line_ids.filtered(lambda line: line.line_type == "clawback")
        if not (raised or recovered):
            return ""
        parts = []
        if raised:
            parts.append(
                "Clawbacks raised by this computation, approved with this run: %s."
                % "; ".join(
                    "%s %.2f BDT (%s on %s, from the %s run)"
                    % (
                        cb.employee_id.name,
                        cb.amount,
                        cb.trigger,
                        cb.service_order_id.display_name,
                        cb.source_run_id.period,
                    )
                    for cb in raised
                )
            )
        if recovered:
            parts.append(
                "Clawbacks recovered from this run's incentives: %s."
                % "; ".join(
                    "%s %.2f BDT (%s)"
                    % (line.employee_id.name, -line.amount, line.clawback_id.name)
                    for line in recovered
                )
            )
        return " ".join(parts)

    def action_request_approval(self, justification=None):
        # a bare bool(mapped("void_pending")) is always True for a non-empty
        # recordset (a one-item list of False is truthy), which skipped the
        # dispute window and the adjustments gate on every request
        voiding = any(self.mapped("void_pending"))
        for rec in self:
            if rec.void_pending:
                continue  # M57-F19: the routed void request of an approved run.
            if rec.state != "computed" or not rec.line_ids:
                raise UserError("Compute the run before requesting its approval.")
        if not voiding:
            self._fix_assert_disputes_settled(requesting=True)
            self._fix_assert_adjustments_applied()
        # M57-F11: the clawbacks stand on the approval statement the approver
        # decides on (request justification + the run's chatter).
        parts = []
        for rec in self:
            part = rec._fix_clawback_statement()
            if part:
                parts.append(part)
                rec.message_post(body="Approval statement — %s" % part)
        statement = " ".join(parts)
        if statement:
            justification = "%s | %s" % (justification, statement) if justification else statement
        return super().action_request_approval(justification=justification)

    def action_request_void(self, justification=None):
        """M57-F19: a routed void of an approved run before payment. Only while
        no line has reached a payslip; a second person (never the requester,
        the computer, the original approver or anyone with a line) decides it
        through the same M63 inbox."""
        require_group(self.env, OFFICER, "Requesting that a run be voided")
        for rec in self:
            if rec.state != "approved":
                raise UserError("Only an approved run can be voided, before it is paid.")
            if rec.approval_state == "pending":
                raise UserError("%s already has a decision waiting." % rec.display_name)
            attached = rec.sudo().line_ids.filtered("applied_to_payslip")
            if attached:
                raise UserError(
                    "%d line(s) of the %s run are already on a payslip: a paid run is not "
                    "voided, it is corrected." % (len(attached), rec.period)
                )
            rec._guarded().write(
                {
                    "void_pending": True,
                    "void_requested_by_id": self.env.user.id,
                    "void_reason": justification or False,
                }
            )
        return self.action_request_approval(justification=justification)

    def _fix_apply_void(self, rec):
        """The routed void decision: the run's lines go, the clawbacks it
        raised are released for a later run, its adjustments return to
        approved-unapplied, and the run is void before any payment."""
        attached = rec.sudo().line_ids.filtered("applied_to_payslip")
        if attached:
            raise UserError(
                "%d line(s) are already on a payslip: the run cannot be voided." % len(attached)
            )
        rec.line_ids._guarded().unlink()
        self.env["fix.incentive.adjustment"].sudo().search(
            [("applied_run_id", "=", rec.id)]
        )._guarded().write({"state": "approved", "applied_run_id": False, "applied_line_id": False})
        rec._guarded().write(
            {
                "state": "void",
                "void_pending": False,
                "voided_by_id": rec._people_decider().id,
                "voided_at": fields.Datetime.now(),
                "approval_state": "approved",
            }
        )
        rec.message_post(
            body="Run voided before payment by %s (requested by %s): %s"
            % (rec.voided_by_id.name, rec.void_requested_by_id.name, rec.void_reason or "")
        )
        return True

    def action_approve(self):
        """Run by the approval engine from the approver's inbox task: the
        approval of the computation, or of a requested void (M57-F19)."""
        self._approval_assert_routed()
        self._people_assert_not_conflicted()
        for rec in self:
            if rec.void_pending:
                if rec.state != "approved":
                    raise UserError("Only an approved run can be voided.")
                rec._fix_apply_void(rec)
                continue
            if rec.state != "computed":
                raise UserError("Only a computed incentive run can be approved.")
            self._fix_assert_disputes_settled()
            self._fix_assert_adjustments_applied()
            version = rec.sudo().scheme_version_id
            if version and version.state != "approved":
                raise UserError("Scheme version %s is no longer approved." % version.display_name)
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
    line_type = fields.Selection(
        [("incentive", "Incentive"), ("clawback", "Clawback Recovery")],
        default="incentive",
        required=True,
        readonly=True,
    )
    gross_amount = fields.Monetary(
        string="Banded Amount",
        currency_field="currency_id",
        readonly=True,
        help="The scheme band's amount for the score, before proration.",
    )
    proration_factor = fields.Float(string="Proration", digits=(3, 4), readonly=True, default=1.0)
    eligible_days = fields.Integer(string="Paid Days", readonly=True)
    period_days = fields.Integer(string="Days in Period", readonly=True)
    eligible = fields.Boolean(string="Eligible", readonly=True, default=True)
    eligibility_note = fields.Char(string="Eligibility / Proration Basis", readonly=True)
    clawback_id = fields.Many2one(
        "fix.incentive.clawback", string="Clawback Recovered", readonly=True, ondelete="restrict"
    )
    amount = fields.Monetary(string="Amount", currency_field="currency_id", readonly=True)
    payslip_ref_id = fields.Integer(string="Applied Payslip ID", readonly=True)
    applied_to_payslip = fields.Boolean(string="Applied to Payslip", default=False, readonly=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    run_state = fields.Selection(related="run_id.state", string="Run State")
    dispute_ids = fields.One2many("fix.incentive.dispute", "line_id", string="Disputes")
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    def _fix_guarded_fields(self) -> set:
        # A line is what the computation produced; nobody types one.
        return super()._fix_guarded_fields() | {
            "run_id",
            "scorecard_id",
            "employee_id",
            "line_type",
            "gross_amount",
            "proration_factor",
            "eligible_days",
            "period_days",
            "eligible",
            "eligibility_note",
            "clawback_id",
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

    def action_raise_dispute(self, reason=None, dispute=None):
        """BRU-PIC-12, FR-PIC-014: the employee disputes their own computed
        line, with a reason, inside the window. A plain employee holds no
        write access to M57 records (RAP X-02): this method checks who asks
        and creates the dispute itself."""
        reason = str((dispute if dispute not in (None, False, "") else reason) or "").strip()
        if not reason:
            raise UserError("Say what is wrong with the figure, and on what evidence.")
        self.check_access("read")  # record rules: the caller's own lines only
        today = fields.Date.context_today(self)
        Dispute = self.env["fix.incentive.dispute"].sudo()._guarded()
        created = Dispute.browse()
        for line in self.sudo():
            if not self.env.su and line.employee_id.user_id != self.env.user:
                raise AccessError("Only %s disputes their incentive line." % line.employee_id.name)
            run = line.run_id
            if run.state != "computed":
                raise UserError(
                    "The %s run is %s: a line is disputed while the run is computed and "
                    "not yet approved." % (run.period, run.state)
                )
            if not run.dispute_deadline:
                raise UserError("No dispute window is ruled for incentive runs.")
            if today > run.dispute_deadline:
                raise UserError(
                    "The dispute window for %s closed on %s." % (run.period, run.dispute_deadline)
                )
            if line.dispute_ids.filtered(lambda d: d.state == "open"):
                raise UserError("This line already has an open dispute.")
            if run.approval_state == "pending":
                run._approval_void("an employee disputed their line")
            created |= Dispute.create(
                {
                    "company_id": line.company_id.id,
                    "run_id": run.id,
                    "line_id": line.id,
                    "employee_id": line.employee_id.id,
                    "reason": reason,
                    "raised_by_id": self.env.user.id,
                    "raised_at": fields.Datetime.now(),
                }
            )
            officer = run.computed_by_id
            if officer and officer.active:
                run.activity_schedule(
                    "mail.mail_activity_data_todo",
                    date_deadline=today,
                    summary="Incentive dispute: %s" % line.employee_id.name,
                    note=reason,
                    user_id=officer.id,
                )
        return {"dispute_ids": created.ids}

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
    def _fix_check_amount(self, grade, amount, company=None, what="The salary", exception=None):
        """I7: refuse `amount` outside the grade's band. No configured band
        (none, or its ranges empty) means no check: the band is the rule.

        M57-F18 / D27: an approved fix.band.exception for this employee and
        grade (and up to its figure) lets the amount through - the CFO tier
        decision the owner asked for."""
        band = self._fix_band_for(grade, company)
        if not band:
            return True
        lo, hi = band.range_min, band.range_max
        if not (lo <= (amount or 0.0) <= hi):
            if exception and exception._fix_covers(amount, grade):
                return True
            raise ValidationError(
                "%s of %.2f is outside the %s band for grade %s (%.2f to %.2f). "
                "A salary outside the band needs an approved above-band exception "
                "(CFO tier) or the band changed by the Compensation Manager."
                % (what, amount or 0.0, band.name, grade, lo, hi)
            )
        return True
