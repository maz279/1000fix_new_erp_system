# M43 §5.2 — Forecasting & forecast management (CD-M43-01).
# Sub-modules 3 "Forecast Orchestration" and 4 "Accuracy Tracking" capture here.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28


class FixPlanningRun(models.Model):
    """§8.1 / FR-DPL-010, FR-DPL-015: one planning review cycle. A-class and
    critical plans need the consensus sign-off of procurement, operations
    and finance before the cycle closes."""
    _name = "fix.planning.run"
    _description = "Planning Review Cycle"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "period_start desc, id desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(string="Cycle Name", required=True, tracking=True)
    name_bn = fields.Char(string="চক্রের নাম (বাংলা)")
    run_type = fields.Selection([("full", "Full Network"), ("incremental", "Incremental")],
                                string="Run Type", required=True, default="full")
    scope = fields.Char(string="Scope (category / location)")
    period_start = fields.Date(string="Period Start", required=True)
    period_end = fields.Date(string="Period End", required=True)
    horizon_months = fields.Integer(string="Horizon (months)", default=6,
                                    help="Lead time plus review period (FR-DPL-010)")
    started_at = fields.Datetime(string="Started At", readonly=True)
    completed_at = fields.Datetime(string="Completed At", readonly=True)
    parts_processed = fields.Integer(string="Parts Processed", readonly=True)
    forecasts_generated = fields.Integer(string="Forecasts Generated", readonly=True)
    degraded_count = fields.Integer(string="Degraded Forecasts", readonly=True)
    procurement_signoff_id = fields.Many2one("res.users", string="Procurement Sign-off", readonly=True)
    operations_signoff_id = fields.Many2one("res.users", string="Operations Sign-off", readonly=True)
    finance_signoff_id = fields.Many2one("res.users", string="Finance Sign-off", readonly=True)
    notes = fields.Text(string="Review Notes")
    state = fields.Selection([
        ("draft", "Draft"),
        ("running", "Running"),
        ("review", "In Review"),
        ("signed_off", "Signed Off"),
        ("cancelled", "Cancelled"),
    ], default="draft", required=True, tracking=True)

    @api.constrains("period_start", "period_end", "horizon_months")
    def _check_period(self):
        for rec in self:
            if rec.period_end and rec.period_start and rec.period_end < rec.period_start:
                raise ValidationError("The cycle cannot end before it starts.")
            if rec.horizon_months <= 0:
                raise ValidationError("The forecast horizon must be at least one month.")

    def action_start(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft cycle can be started.")
            rec.write({"state": "running", "started_at": fields.Datetime.now()})
            publish(self.env, "demand_plan.run.started", "fix.planning.run", rec.id,
                    {"name": rec.name, "type": rec.run_type, "scope": rec.scope or ""})

    def action_to_review(self):
        for rec in self:
            if rec.state != "running":
                raise UserError("Only a running cycle moves to review.")
            rec.write({"state": "review", "completed_at": fields.Datetime.now()})

    def _sign(self, field):
        for rec in self:
            if rec.state != "review":
                raise UserError("Sign-off happens while the cycle is in review.")
            rec[field] = self.env.user
            if rec.procurement_signoff_id and rec.operations_signoff_id and rec.finance_signoff_id:
                rec.state = "signed_off"
                publish(self.env, "demand_plan.run.signed_off", "fix.planning.run", rec.id,
                        {"name": rec.name})

    def action_sign_procurement(self):
        self._sign("procurement_signoff_id")

    def action_sign_operations(self):
        self._sign("operations_signoff_id")

    def action_sign_finance(self):
        self._sign("finance_signoff_id")

    def action_cancel(self):
        for rec in self:
            if rec.state == "signed_off":
                raise UserError("A signed-off cycle cannot be cancelled.")
            rec.state = "cancelled"


class FixForecastOverride(models.Model):
    """FR-DPL-014 / BRU-DPL-06: a planner override needs a rationale; both
    the statistical and the final number are retained."""
    _name = "fix.forecast.override"
    _description = "Forecast Override"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    demand_plan_id = fields.Many2one("fix.demand.plan", string="Demand Plan",
                                     required=True, ondelete="cascade", index=True)
    original_value = fields.Float(string="Statistical Forecast", readonly=True)
    override_value = fields.Float(string="Override Forecast", required=True)
    driver_type = fields.Selection([
        ("installed_base", "Installed Base"),
        ("contract", "Contract / AMC Schedule"),
        ("campaign", "Warranty Campaign"),
        ("seasonality", "Seasonality"),
        ("branch_opening", "Branch Opening"),
        ("market_intel", "Market Intelligence"),
    ], string="Driver")
    rationale = fields.Text(string="Rationale", required=True)
    rationale_bn = fields.Text(string="যুক্তি (বাংলা)")
    planner_id = fields.Many2one("res.users", string="Planner",
                                 default=lambda self: self.env.user, readonly=True)
    applied_at = fields.Datetime(string="Applied At", readonly=True)
    state = fields.Selection([("draft", "Draft"), ("applied", "Applied"), ("withdrawn", "Withdrawn")],
                             default="draft", required=True, tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            plan = self.env["fix.demand.plan"].browse(vals.get("demand_plan_id"))
            if plan:
                vals.setdefault("original_value", plan.forecast_quantity)
        return super().create(vals_list)

    @api.constrains("override_value")
    def _check_value(self):
        for rec in self:
            if rec.override_value < 0:
                raise ValidationError("A forecast cannot be negative.")

    def action_apply(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft override can be applied.")
            if not (rec.rationale or "").strip():
                raise UserError("A forecast override requires a recorded rationale (BRU-DPL-06).")
            rec.write({"state": "applied", "applied_at": fields.Datetime.now()})
            rec.demand_plan_id.override_quantity = rec.override_value
            publish(self.env, "demand_plan.forecast.overridden", "fix.forecast.override",
                    rec.id, {"plan": rec.demand_plan_id.name,
                             "statistical": rec.original_value,
                             "final": rec.override_value})

    def action_withdraw(self):
        for rec in self:
            if rec.state == "applied" and rec.demand_plan_id.override_quantity == rec.override_value:
                rec.demand_plan_id.override_quantity = 0.0
            rec.state = "withdrawn"


class FixDemandDriver(models.Model):
    """FR-DPL-013: a known influence on demand that forecasts adjust for."""
    _name = "fix.demand.driver"
    _description = "Demand Driver"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_from desc, id desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(string="Driver", required=True)
    name_bn = fields.Char(string="চালক (বাংলা)")
    driver_type = fields.Selection([
        ("installed_base", "Installed Base"),
        ("contract", "Contract / AMC Schedule"),
        ("campaign", "Warranty Campaign"),
        ("seasonality", "Seasonality"),
        ("branch_opening", "Branch Opening"),
    ], string="Driver Type", required=True, default="seasonality")
    source_module = fields.Selection([
        ("M17", "M17 Device Registry"), ("M08", "M08 Contracts"),
        ("M09", "M09 Warranty"), ("M43", "M43 Planner"),
    ], string="Source Module", default="M43")
    source_ref = fields.Char(string="Source Reference")
    spare_part_id = fields.Many2one("fix.spare.part", string="Spare Part (blank = all)")
    location_id = fields.Many2one("fix.stock.location", string="Location (blank = network)")
    date_from = fields.Date(string="From", required=True)
    date_to = fields.Date(string="To", required=True)
    expected_impact_pct = fields.Float(string="Expected Impact (%)")
    active = fields.Boolean(default=True)

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for rec in self:
            if rec.date_to < rec.date_from:
                raise ValidationError("A driver cannot end before it starts.")


class FixForecastAccuracyReview(models.Model):
    """Sub-module 4 capture. Accuracy itself is MEASURED (FR-DPL-016) and
    cannot be suppressed or edited (BRU-DPL-16); this note records the
    planner's review of a measured result and the corrective action taken,
    alongside — never instead of — the measurement."""
    _name = "fix.forecast.accuracy.review"
    _description = "Accuracy Review Note"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "period_end desc, id desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    period_start = fields.Date(string="Period Start", required=True)
    period_end = fields.Date(string="Period End", required=True)
    segment = fields.Char(string="Segment (e.g. AX, job-stopping)")
    forecast_method = fields.Selection([
        ("ets", "Exponential Smoothing (ETS)"),
        ("croston_sba", "Croston / SBA"),
        ("bootstrap", "Lead-Time Demand Bootstrap"),
        ("fallback", "Degraded Local Fallback"),
    ], string="Method Reviewed")
    planner_id = fields.Many2one("res.users", string="Planner Reviewed")
    horizon_months = fields.Integer(string="Horizon (months)", default=1)
    measured_mape = fields.Float(string="Measured MAPE (%)",
                                 help="As published by accuracy tracking — read from the measure, not re-keyed")
    measured_bias = fields.Float(string="Measured Bias (%)")
    finding = fields.Text(string="Finding", required=True)
    finding_bn = fields.Text(string="পর্যবেক্ষণ (বাংলা)")
    corrective_action = fields.Selection([
        ("none", "No Action"),
        ("method_reselection", "Propose Method Re-selection"),
        ("parameter_review", "Review Parameters"),
        ("data_cleansing", "Cleanse History"),
        ("driver_update", "Update Demand Drivers"),
    ], string="Corrective Action", required=True, default="none")
    reviewer_id = fields.Many2one("res.users", string="Reviewer",
                                  default=lambda self: self.env.user, readonly=True)
    state = fields.Selection([("draft", "Draft"), ("submitted", "Submitted"), ("closed", "Closed")],
                             default="draft", required=True, tracking=True)

    @api.constrains("period_start", "period_end")
    def _check_period(self):
        for rec in self:
            if rec.period_end < rec.period_start:
                raise ValidationError("The review period cannot end before it starts.")

    def action_submit(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft review note can be submitted.")
            rec.state = "submitted"
            if rec.corrective_action == "method_reselection":
                # FR-DPL-017: propose the change to the planner and to M26
                publish(self.env, "demand_plan.method.reselection_proposed",
                        "fix.forecast.accuracy.review", rec.id,
                        {"segment": rec.segment or "", "method": rec.forecast_method or "",
                         "mape": rec.measured_mape, "bias": rec.measured_bias})

    def action_close(self):
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Only a submitted review note can be closed.")
            rec.state = "closed"
