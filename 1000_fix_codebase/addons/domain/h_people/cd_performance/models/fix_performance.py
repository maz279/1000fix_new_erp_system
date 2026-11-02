# fix_performance — M57: scorecard, incentives, compensation (P08-M04).
from odoo import api, fields, models
from odoo.exceptions import UserError

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


class FixPerformanceScorecard(models.Model):
    _name = "fix.performance.scorecard"
    _description = "Technician Scorecard"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "period desc, employee_id"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    period = fields.Char(required=True, help="YYYY-MM")
    first_time_fix = fields.Float(string="First-Time Fix (0-1)")
    sla_hit = fields.Float(string="SLA Hit Rate (0-1)")
    csat = fields.Float(string="CSAT (normalised 0-1)")
    rework_rate = fields.Float(string="Rework Rate (0-1)")
    rework_30d_rate = fields.Float(
        string="30-Day Rework Rate (0-1)",
        default=0.0,
        help="RAP-M57-02: >3% triggers clawback penalty ramp",
    )
    salvage_value = fields.Float(
        string="Component Salvage Value (BDT)",
        default=0.0,
        help="Value of recovered/repaired sub-assemblies",
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

    def action_publish(self):
        for rec in self:
            publish(
                self.env,
                "scorecard.published",
                "fix.performance.scorecard",
                rec.id,
                {"employee": rec.employee_id.name, "period": rec.period, "score": rec.score},
            )

    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")


class FixIncentiveRun(models.Model):
    _name = "fix.incentive.run"
    _description = "Incentive Run"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "period desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    period = fields.Char(required=True)
    band_base = fields.Monetary(
        string="Band Base",
        currency_field="currency_id",
        required=True,
        groups="base.group_system",
        help="T5-protected compensation input (05-04 4-5)",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    state = fields.Selection(
        [("draft", "Draft"), ("computed", "Computed"), ("applied", "Applied to Payroll")],
        default="draft",
        required=True,
        tracking=True,
    )
    line_ids = fields.One2many("fix.incentive.line", "run_id", string="Incentive Lines")
    total = fields.Monetary(compute="_compute_total", currency_field="currency_id", string="Total")

    @api.depends("line_ids.amount")
    def _compute_total(self):
        for rec in self:
            rec.total = sum(rec.line_ids.mapped("amount"))

    def action_compute(self):
        """One line per scorecard in the period; the banded amount."""
        for rec in self:
            if rec.state != "draft":
                raise UserError("Compute runs from draft only")
            scorecards = self.env["fix.performance.scorecard"].search([("period", "=", rec.period)])
            if not scorecards:
                raise UserError("No scorecards for %s" % rec.period)
            self.env["fix.incentive.line"].create(
                [
                    {
                        "run_id": rec.id,
                        "scorecard_id": sc.id,
                        "employee_id": sc.employee_id.id,
                        "amount": incentive_amount(sc.score, rec.band_base),
                    }
                    for sc in scorecards
                ]
            )
            rec.state = "computed"

    def action_apply(self):
        """The engine FEEDS payroll: lines publish incentive.granted; the
        payroll period's payslips pick the amount up per employee."""
        for rec in self:
            if rec.state != "computed":
                raise UserError("Compute before applying")
            for line in rec.line_ids:
                if "fix.payslip" in self.env and not line.applied_to_payslip:
                    Payslip = self.env["fix.payslip"]
                    slip = Payslip.search(
                        [
                            ("employee_id", "=", line.employee_id.id),
                            ("period_id.state", "in", ("draft", "calculated")),
                            ("period_id.name", "ilike", rec.period),
                        ],
                        order="id desc",
                        limit=1,
                    )
                    if not slip and len(rec.period or "") == 7 and "-" in rec.period:
                        slip = Payslip.search(
                            [
                                ("employee_id", "=", line.employee_id.id),
                                ("period_id.state", "in", ("draft", "calculated")),
                            ],
                            order="id desc",
                        ).filtered(
                            lambda s, period=rec.period: s.period_id.period_start
                            and s.period_id.period_start.strftime("%Y-%m") == period
                        )[:1]
                    if slip:
                        slip.write({"incentive": line.amount})
                        line.write({"payslip_ref_id": slip.id, "applied_to_payslip": True})
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
                        "payslip_id": line.payslip_ref_id or 0,
                    },
                )
            rec.state = "applied"

    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")


class FixIncentiveLine(models.Model):
    _name = "fix.incentive.line"
    _description = "Incentive Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    run_id = fields.Many2one("fix.incentive.run", required=True, ondelete="cascade")
    scorecard_id = fields.Many2one("fix.performance.scorecard", required=True)
    employee_id = fields.Many2one("hr.employee", required=True)
    amount = fields.Monetary(string="Amount", currency_field="currency_id")
    payslip_ref_id = fields.Integer(string="Applied Payslip ID", readonly=True)
    applied_to_payslip = fields.Boolean(string="Applied to Payslip", default=False, readonly=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )

    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")


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
        string="Range Min", currency_field="currency_id", groups="base.group_system"
    )
    range_mid = fields.Monetary(
        string="Range Mid", currency_field="currency_id", groups="base.group_system"
    )
    range_max = fields.Monetary(
        string="Range Max", currency_field="currency_id", groups="base.group_system"
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )

    @api.constrains("range_min", "range_mid", "range_max")
    def _check_range(self):
        for rec in self:
            if not (rec.range_min <= rec.range_mid <= rec.range_max):
                raise UserError("Band range must be min <= mid <= max")

    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
