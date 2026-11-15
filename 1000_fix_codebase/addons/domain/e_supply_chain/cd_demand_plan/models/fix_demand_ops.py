# fix_demand_ops — M43: forecast cycles, segmentation, safety-stock / ROP
# policy versions, review cycles, rebalance proposals and what-if scenarios.
#
# A06 audit (2026-11-03) and what changed here:
#  - R6 / M43-3 / M43-6 / M43-9: a forecast is COMPUTED from M15 consumption
#    (moving average over a stored window of months); the method / source
#    labels say what computed it; a planner override keeps the statistical
#    value beside it and needs a rationale; actuals, variance and MAPE come
#    from M15 consumption, never typed; one forecast per product / location /
#    month; approval by an approver who did not prepare it; frozen after.
#  - M43-7 / M43-8: a policy's demand statistics come from M15 history; its
#    parameters are versioned (a change is a new draft version); activation of
#    an A-class, critical or unclassified item needs a Demand Plan Approver
#    other than the preparer; one active policy per part / location; the
#    computed ROP / target are published to the M15 reorder rule.
#  - M43-10: a rebalance names real M15 locations; approval (by an approver
#    who did not propose it) creates a draft M15 transfer; no savings claim.
#  - M43-11: what-if reads the policy and applies the lead-time delta; a
#    review cycle is completed by its owner with an outcome.
import inspect
from datetime import timedelta
from math import ceil

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_demand_common import (
    APPROVER,
    CFG_ABC_A_SHARE,
    CFG_ABC_B_SHARE,
    CFG_FORECAST_MIN_HISTORY,
    CFG_FORECAST_WINDOW,
    CFG_LEAD_TIME_WINDOW_DAYS,
    CFG_POLICY_HISTORY_DAYS,
    CFG_REVIEW_PERIOD_DAYS,
    CFG_SEGMENT_WINDOW_MONTHS,
    CFG_XYZ_X_CV,
    CFG_XYZ_Y_CV,
    PERIOD_RE,
    PLANNER,
    Z_FACTORS,
    add_months,
    consumed_by_day,
    consumed_by_month,
    consumed_value,
    has_role,
    has_usable_history,
    mean_and_stddev,
    month_end,
    month_start,
    observed_lead_times,
    on_hand,
    param,
    period_of,
    refuse_self_decision,
    require_role,
    safety_stock,
)

# kept for importers of the old module constant
_Z_FACTORS = Z_FACTORS


def _refuse_frozen(rec, vals, names, reason):
    changed = [n for n in names & set(vals) if rec._fix_guard_differs(n, vals[n], rec[n])]
    if changed:
        labels = ", ".join(sorted(rec._fields[n].string or n for n in changed))
        raise UserError("%s cannot be changed on %s: %s." % (labels, rec.display_name, reason))
    return changed


def _changed(rec, vals, names):
    return [n for n in names & set(vals) if rec._fix_guard_differs(n, vals[n], rec[n])]


# =====================================================================
# Spare part: what M43 publishes to M15 and M41 (step 3)
# =====================================================================
class FixSparePartDemandClass(models.Model):
    _inherit = "fix.spare.part"

    demand_abc_class = fields.Selection(
        [("a", "A"), ("b", "B"), ("c", "C")], string="Demand ABC Class", readonly=True, copy=False
    )
    demand_xyz_class = fields.Selection(
        [("x", "X"), ("y", "Y"), ("z", "Z")], string="Demand XYZ Class", readonly=True, copy=False
    )
    demand_criticality = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")],
        string="Demand Criticality",
        readonly=True,
        copy=False,
    )
    demand_classified_on = fields.Date(string="Demand Classified On", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "demand_abc_class",
            "demand_xyz_class",
            "demand_criticality",
            "demand_classified_on",
        }


# =====================================================================
# Forecast
# =====================================================================
FORECAST_INPUTS = {
    "product_id",
    "part_id",
    "location_id",
    "period",
    "window_months",
    "has_override",
    "override_qty",
    "override_rationale",
    "override_driver_id",
    "company_id",
}
FORECAST_HISTORY_KEYS = {"product_id", "part_id", "location_id", "period", "window_months"}


class FixDemandForecast(models.Model):
    _name = "fix.demand.forecast"
    _description = "Demand Forecast"
    _inherit = ["fix.guarded.mixin"]
    _order = "period desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    product_id = fields.Many2one(
        "product.product", string="Product", required=True, ondelete="cascade", index=True
    )
    part_id = fields.Many2one(
        "fix.spare.part", string="M15 Spare Part", index=True, help="Whose consumption is history"
    )
    location_id = fields.Many2one(
        "fix.stock.location", string="Stock Location", index=True, help="Empty = all locations"
    )
    period = fields.Char(required=True, help="YYYY-MM")
    window_months = fields.Integer(
        string="Moving-Average Window (months)",
        default=lambda self: self._default_window(),
        help="Months of M15 consumption before the period that the moving average uses",
    )
    statistical_qty = fields.Float(string="Statistical Forecast", readonly=True)
    history_months_with_data = fields.Integer(string="History Months With Data", readonly=True)
    history_detail = fields.Char(string="History Used", readonly=True)
    computed_on = fields.Datetime(string="Computed On", readonly=True)
    has_override = fields.Boolean(string="Planner Override")
    override_qty = fields.Float(string="Override Qty")
    override_rationale = fields.Text(string="Override Rationale")
    forecast_qty = fields.Float(
        string="Forecast Qty", compute="_compute_final", store=True, readonly=True
    )
    actual_qty = fields.Float(
        string="Actual Qty", compute="_compute_actuals", help="M15 consumption in the period"
    )
    period_closed = fields.Boolean(compute="_compute_actuals")
    variance = fields.Float(string="Variance", compute="_compute_actuals")
    abs_error_pct = fields.Float(string="Absolute Error %", compute="_compute_actuals")
    method = fields.Selection(
        [
            ("moving_average", "Moving Average"),
            # labelled, never set: the M26 forecast engine is not built
            ("exponential", "Exponential Smoothing (M26, not built)"),
            ("seasonal", "Seasonal (M26, not built)"),
            ("manual", "Manual"),
        ],
        required=True,
        default="manual",
        compute="_compute_final",
        store=True,
        readonly=True,
    )
    source = fields.Selection(
        [("history", "History-derived"), ("model", "Model (M26, not built)"), ("manual", "Manual")],
        required=True,
        default="manual",
        compute="_compute_final",
        store=True,
        readonly=True,
    )
    confidence_pct = fields.Float(string="Confidence %", default=0.0)
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("published", "Published")],
        required=True,
        default="draft",
    )
    prepared_by_id = fields.Many2one(
        "res.users", string="Prepared By", default=lambda self: self.env.user, readonly=True
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True)
    approved_on = fields.Datetime(readonly=True)
    notes = fields.Char()

    @api.model
    def _default_window(self):
        return param(self.env, CFG_FORECAST_WINDOW, 3, int)

    # ---------------------------------------------------------------- guard
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "statistical_qty",
            "history_months_with_data",
            "history_detail",
            "computed_on",
            "forecast_qty",
            "method",
            "source",
            "actual_qty",
            "variance",
            "abs_error_pct",
            "prepared_by_id",
            "approved_by_id",
            "approved_on",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        rec = self[:1]
        if rec and rec.state != "draft":
            locked |= FORECAST_INPUTS | {"notes", "confidence_pct"}
        return locked

    def write(self, vals):
        stale = self.browse()
        edited = self.browse()
        if self and not self._fix_guard_open():
            for rec in self:
                if rec.state != "draft":
                    _refuse_frozen(
                        rec, vals, FORECAST_INPUTS, "it is %s; a forecast is frozen" % rec.state
                    )
                    continue
                if _changed(rec, vals, FORECAST_INPUTS):
                    edited |= rec
                if _changed(rec, vals, FORECAST_HISTORY_KEYS):
                    stale |= rec
        res = super().write(vals)
        if edited:
            edited._guarded().write({"prepared_by_id": self.env.user.id})
        if stale:
            stale._guarded().write(
                {
                    "statistical_qty": 0.0,
                    "history_months_with_data": 0,
                    "history_detail": False,
                    "computed_on": False,
                }
            )
        return res

    # ---------------------------------------------------------------- computes
    @api.depends("statistical_qty", "computed_on", "has_override", "override_qty")
    def _compute_final(self):
        for rec in self:
            if rec.has_override:
                rec.forecast_qty = rec.override_qty
                rec.method = "manual"
                rec.source = "manual"
            elif rec.computed_on:
                rec.forecast_qty = rec.statistical_qty
                rec.method = "moving_average"
                rec.source = "history"
            else:
                rec.forecast_qty = 0.0
                rec.method = "manual"
                rec.source = "manual"

    @api.depends("part_id", "location_id", "period", "forecast_qty", "company_id")
    def _compute_actuals(self):
        today = fields.Date.today()  # M15 consumed_at is UTC
        for rec in self:
            actual, closed = 0.0, False
            if rec.part_id and rec.period and PERIOD_RE.match(rec.period):
                first = month_start(rec.period)
                closed = month_end(first) < today
                actual = consumed_by_month(
                    rec.env,
                    rec.company_id or rec.env.company,
                    rec.part_id,
                    rec.location_id,
                    first,
                    1,
                )[0]
            rec.actual_qty = round(actual, 3)
            rec.period_closed = closed
            var = actual - (rec.forecast_qty or 0.0)
            rec.variance = round(var, 3)
            base = actual or rec.forecast_qty
            rec.abs_error_pct = round(abs(var) / base * 100.0, 1) if base else 0.0

    # ---------------------------------------------------------------- constraints
    @api.constrains("period")
    def _check_period(self):
        for rec in self:
            if not PERIOD_RE.match(rec.period or ""):
                raise ValidationError("Period %r is not a YYYY-MM month." % (rec.period,))

    @api.constrains("product_id", "part_id", "location_id", "period", "company_id")
    def _check_unique_period(self):
        for rec in self:
            domain = [
                ("id", "!=", rec.id),
                ("company_id", "=", rec.company_id.id),
                ("location_id", "=", rec.location_id.id),
                ("period", "=", rec.period),
            ]
            if rec.part_id:
                domain += [
                    "|",
                    ("product_id", "=", rec.product_id.id),
                    ("part_id", "=", rec.part_id.id),
                ]
            else:
                domain.append(("product_id", "=", rec.product_id.id))
            if self.sudo().search_count(domain):
                raise ValidationError(
                    "There is already a forecast for %s in %s (one forecast per product, "
                    "location and month)." % (rec.product_id.display_name, rec.period)
                )

    @api.constrains("has_override", "override_qty", "override_rationale", "window_months")
    def _check_override(self):
        for rec in self:
            if rec.has_override and not (rec.override_rationale or "").strip():
                raise ValidationError("A forecast override needs a rationale (BRU-DPL-06).")
            if rec.has_override and rec.override_qty < 0:
                raise ValidationError("A forecast override cannot be negative.")
            if rec.window_months < 1 or rec.window_months > 36:
                raise ValidationError("The moving-average window is 1 to 36 months.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.demand.forecast") or "DFC/New"
                )
        return super().create(vals_list)

    # ---------------------------------------------------------------- actions
    def action_compute_forecast(self):
        """Moving average of the M15 consumption of the `window_months` months
        before the period (months without consumption count as zero)."""
        require_role(self.env, PLANNER, what="Computing a forecast")
        min_months = param(self.env, CFG_FORECAST_MIN_HISTORY, 2, int)
        for rec in self:
            if rec.state != "draft":
                raise UserError("Compute a draft forecast")
            if not rec.part_id:
                raise UserError(
                    "Forecast %s has no M15 spare part, so there is no consumption history "
                    "to compute from." % rec.name
                )
            window = rec.window_months
            first = add_months(month_start(rec.period), -window)
            buckets = consumed_by_month(
                rec.env, rec.company_id, rec.part_id, rec.location_id, first, window
            )
            # T-01: applied outlier / censored-demand adjustments are an overlay
            # on the M15 series (marked * in the history), never an edit of it
            buckets, adjusted = self.env["fix.demand.adjustment"]._overlay(
                rec.company_id, rec.part_id, rec.location_id, first, buckets
            )
            with_data = sum(1 for b in buckets if b > 0)
            if with_data < min_months:
                raise UserError(
                    "Forecast %s is not ready for a statistical forecast: %d of the %d months "
                    "before %s have M15 consumption (minimum %d, %s). Record a planner "
                    "override with its rationale instead."
                    % (
                        rec.name,
                        with_data,
                        window,
                        rec.period,
                        min_months,
                        CFG_FORECAST_MIN_HISTORY,
                    )
                )
            detail = ", ".join(
                "%s: %g%s"
                % (
                    period_of(add_months(first, i)),
                    b,
                    "*" if period_of(add_months(first, i)) in adjusted else "",
                )
                for i, b in enumerate(buckets)
            )
            rec._guarded().write(
                {
                    "statistical_qty": round(sum(buckets) / window, 3),
                    "history_months_with_data": with_data,
                    "history_detail": detail,
                    "computed_on": fields.Datetime.now(),
                }
            )
        return True

    def action_approve(self):
        require_role(self.env, APPROVER, what="Approving a forecast")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Approve a draft forecast")
            refuse_self_decision(
                self.env, rec.create_uid | rec.prepared_by_id, "Forecast %s" % rec.name
            )
            if not rec.part_id:
                raise UserError(
                    "Forecast %s has no M15 spare part to measure it against" % rec.name
                )
            if not (rec.computed_on or rec.has_override):
                raise UserError(
                    "Forecast %s is neither computed from history nor overridden with a "
                    "rationale" % rec.name
                )
            if rec.forecast_qty <= 0:
                raise UserError("A forecast needs a positive quantity")
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.user.id,
                    "approved_on": fields.Datetime.now(),
                }
            )
        return True

    def action_reset_draft(self):
        require_role(self.env, PLANNER, APPROVER, what="Re-opening a forecast")
        for rec in self:
            if rec.state != "approved":
                raise UserError("Only an approved, unpublished forecast can be re-opened")
            rec._guarded().write(
                {
                    "state": "draft",
                    "approved_by_id": False,
                    "approved_on": False,
                    "prepared_by_id": self.env.user.id,
                }
            )
        return True

    def action_publish(self):
        require_role(self.env, PLANNER, APPROVER, what="Publishing a forecast")
        for rec in self:
            if rec.state != "approved":
                raise UserError("Publish an approved forecast")
            rec._guarded().write({"state": "published"})
        return True


# =====================================================================
# Segmentation
# =====================================================================
class FixDemandSegment(models.Model):
    _name = "fix.demand.segment"
    _description = "Demand Segmentation"
    _inherit = ["fix.guarded.mixin"]
    _order = "product_id"

    company_id = fields.Many2one(
        "res.company", index=True, default=lambda self: self.env.company, string="Company"
    )
    product_id = fields.Many2one(
        "product.product", string="Product", required=True, ondelete="cascade", index=True
    )
    part_id = fields.Many2one("fix.spare.part", string="M15 Spare Part", index=True)
    abc_class = fields.Selection(
        [("a", "A — High value"), ("b", "B — Medium"), ("c", "C — Low")],
        required=True,
        default="c",
    )
    xyz_class = fields.Selection(
        [("x", "X — Stable"), ("y", "Y — Variable"), ("z", "Z — Erratic")],
        required=True,
        default="z",
    )
    criticality = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")],
        required=True,
        default="medium",
    )
    assigned_on = fields.Date(required=True, default=fields.Date.context_today)
    classified_on = fields.Date(string="Classified On", readonly=True)
    consumption_value = fields.Float(string="Consumption Value (window)", readonly=True)
    demand_cv = fields.Float(string="Demand CV", readonly=True)
    state = fields.Selection(
        [("active", "Active"), ("archived", "Archived")], required=True, default="active"
    )

    _product_unique = models.Constraint("UNIQUE (product_id)", "One segmentation row per product")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "abc_class",
            "xyz_class",
            "assigned_on",
            "classified_on",
            "consumption_value",
            "demand_cv",
            "state",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if not has_role(self.env, APPROVER):
            locked |= {"criticality"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        if not has_role(self.env, APPROVER):
            for vals in vals_list:
                if vals.get("criticality", "medium") != "medium":
                    raise UserError("Item criticality is set by a Demand Plan Approver.")
        return super().create(vals_list)

    def write(self, vals):
        if "criticality" in vals and not has_role(self.env, APPROVER):
            for rec in self:
                if rec.criticality != vals["criticality"]:
                    raise UserError("Item criticality is set by a Demand Plan Approver.")
        res = super().write(vals)
        if "criticality" in vals or "part_id" in vals:
            self.filtered("classified_on")._publish_to_part()
        return res

    def _publish_to_part(self):
        """M43 step 3: the classes reach M15 on the spare part, where M15 and
        M41 read them. The part's own criticality stays M15's master."""
        for rec in self.sudo().filtered("part_id"):
            rec.part_id._guarded().write(
                {
                    "demand_abc_class": rec.abc_class,
                    "demand_xyz_class": rec.xyz_class,
                    "demand_criticality": rec.criticality,
                    "demand_classified_on": rec.classified_on,
                }
            )

    def _is_critical(self) -> bool:
        return self.criticality == "critical" or (
            self.part_id and self.part_id.criticality == "critical"
        )

    @api.model
    def action_classify(self):
        """ABC by consumption value (Pareto shares) and XYZ by the coefficient
        of variation of monthly consumption, over the configured window, for
        every active segment of the company that has an M15 part."""
        require_role(self.env, PLANNER, what="Classifying parts")
        months = param(self.env, CFG_SEGMENT_WINDOW_MONTHS, 12, int)
        a_share = param(self.env, CFG_ABC_A_SHARE, 0.80)
        b_share = param(self.env, CFG_ABC_B_SHARE, 0.95)
        x_cv = param(self.env, CFG_XYZ_X_CV, 0.5)
        y_cv = param(self.env, CFG_XYZ_Y_CV, 1.0)
        today = fields.Date.today()  # M15 consumed_at is UTC
        first = add_months(today.replace(day=1), -months)
        stop = today.replace(day=1)
        company = self.env.company
        segments = self.search(
            [("state", "=", "active"), ("part_id", "!=", False), ("company_id", "=", company.id)]
        )
        values = {
            seg.id: consumed_value(self.env, company, seg.part_id, first, stop) for seg in segments
        }
        total = sum(values.values())
        cumulative = 0.0
        for seg in segments.sorted(lambda s: -values[s.id]):
            value = values[seg.id]
            share_before = cumulative / total if total else 1.0
            cumulative += value
            if value <= 0:
                abc = "c"
            elif share_before < a_share:
                abc = "a"
            elif share_before < b_share:
                abc = "b"
            else:
                abc = "c"
            monthly = consumed_by_month(self.env, company, seg.part_id, False, first, months)
            mean, std = mean_and_stddev(monthly)
            cv = (std / mean) if mean else 0.0
            xyz = "z" if not mean else ("x" if cv <= x_cv else ("y" if cv <= y_cv else "z"))
            seg._guarded().write(
                {
                    "abc_class": abc,
                    "xyz_class": xyz,
                    "consumption_value": round(value, 2),
                    "demand_cv": round(cv, 3),
                    "classified_on": today,
                    "assigned_on": today,
                }
            )
        segments._publish_to_part()
        return True


# =====================================================================
# Policy (versioned)
# =====================================================================
POLICY_INPUTS = {
    "product_id",
    "part_id",
    "location_id",
    "history_days",
    "lead_time_days",
    "service_level_pct",
    "review_period_days",
    "lead_time_window_days",
    "lead_time_override_rationale",
    "moq_qty",
    "pack_size",
    "company_id",
    "provisional_daily_demand",
    "provisional_reason",
}
PROVISIONAL_INPUTS = {"provisional_daily_demand", "provisional_reason"}
POLICY_HISTORY_KEYS = {
    "product_id",
    "part_id",
    "location_id",
    "history_days",
    "lead_time_window_days",
}
LEAD_TIME_SOURCES = [
    ("observed", "Observed (M16 and M44 receipts)"),
    ("typed", "Typed (no receipt history)"),
    ("override", "Planner override"),
]


class FixDemandPolicy(models.Model):
    _name = "fix.demand.policy"
    _description = "Safety Stock & Reorder Policy"
    _inherit = ["fix.guarded.mixin"]
    _order = "product_id, version desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    product_id = fields.Many2one(
        "product.product", string="Product", required=True, ondelete="cascade", index=True
    )
    part_id = fields.Many2one("fix.spare.part", string="M15 Spare Part", index=True)
    location_id = fields.Many2one("fix.stock.location", string="Stock Location", index=True)
    history_days = fields.Integer(
        string="History Window (days)", default=lambda self: self._default_history_days()
    )
    avg_daily_demand = fields.Float(string="Avg Daily Demand", readonly=True)
    demand_stddev = fields.Float(string="Demand Std Dev", readonly=True)
    history_computed_on = fields.Datetime(string="History Computed On", readonly=True)
    # BRU-DPL-01 / M43-3: a part with no history. A planner states a manual daily
    # demand with a reason; a Demand Plan Approver who did not enter it approves
    # it; it stands in for the M15 figure until real history exists.
    provisional_daily_demand = fields.Float(string="Provisional Daily Demand")
    provisional_reason = fields.Char(string="Provisional Demand Reason")
    provisional_state = fields.Selection(
        [
            ("none", "None"),
            ("entered", "Awaiting Approval"),
            ("approved", "Approved"),
            ("expired", "Expired: real history exists"),
        ],
        string="Provisional Demand",
        default="none",
        required=True,
        readonly=True,
    )
    provisional_entered_by_id = fields.Many2one(
        "res.users", string="Provisional Entered By", readonly=True, copy=False
    )
    provisional_approved_by_id = fields.Many2one(
        "res.users", string="Provisional Approved By", readonly=True, copy=False
    )
    provisional_approved_on = fields.Datetime(string="Provisional Approved On", readonly=True)
    lead_time_days = fields.Integer(
        string="Lead Time (days)",
        default=7,
        help="The lead time the formulas use: the observed lead time (rounded up) "
        "unless the planner overrides it with a rationale",
    )
    lead_time_window_days = fields.Integer(
        string="Lead-Time Window (days)",
        default=lambda self: self._default_lead_window(),
        help="M16 and M44 goods receipts of the last N days the observed lead time uses",
    )
    observed_lead_time_days = fields.Float(string="Observed Lead Time (days)", readonly=True)
    lead_time_samples = fields.Integer(string="Lead-Time Samples", readonly=True)
    lead_time_source = fields.Selection(
        LEAD_TIME_SOURCES,
        string="Lead-Time Source",
        compute="_compute_lead_time_source",
        store=True,
        readonly=True,
    )
    lead_time_override_rationale = fields.Text(string="Lead-Time Override Rationale")
    moq_qty = fields.Float(string="Minimum Order Qty", default=0.0)
    pack_size = fields.Float(string="Pack Size", default=0.0, help="0 = no pack rounding")
    service_level_pct = fields.Selection(
        [("90", "90%"), ("95", "95%"), ("98", "98%"), ("99", "99%")],
        required=True,
        default="95",
    )
    review_period_days = fields.Integer(
        string="Review Period (days)",
        default=lambda self: self._default_review_days(),
        help="Demand cover above the ROP that sets the target (max) level",
    )
    safety_stock = fields.Float(compute="_compute_policy", store=True, string="Safety Stock")
    reorder_point = fields.Float(compute="_compute_policy", store=True, string="Reorder Point")
    target_level = fields.Float(compute="_compute_policy", store=True, string="Target (Max) Level")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("paused", "Paused"),
            ("superseded", "Superseded"),
        ],
        required=True,
        default="draft",
    )
    version = fields.Integer(default=1, readonly=True)
    previous_id = fields.Many2one(
        "fix.demand.policy", string="Previous Version", readonly=True, index=True
    )
    approval_required = fields.Boolean(compute="_compute_approval_required")
    prepared_by_id = fields.Many2one(
        "res.users", string="Prepared By", default=lambda self: self.env.user, readonly=True
    )
    approved_by_id = fields.Many2one("res.users", string="Activated By", readonly=True)
    approved_on = fields.Datetime(string="Activated On", readonly=True)
    published_on = fields.Datetime(string="Published to M15", readonly=True)
    published_rule_id = fields.Many2one(
        "fix.reorder.rule", string="M15 Reorder Rule", readonly=True
    )

    _daily_positive = models.Constraint(
        "CHECK (avg_daily_demand >= 0 AND demand_stddev >= 0 AND lead_time_days >= 0)",
        "Demand and lead-time inputs cannot be negative",
    )

    @api.model
    def _default_history_days(self):
        return param(self.env, CFG_POLICY_HISTORY_DAYS, 90, int)

    @api.model
    def _default_lead_window(self):
        return param(self.env, CFG_LEAD_TIME_WINDOW_DAYS, 365, int)

    @api.model
    def _default_review_days(self):
        return param(self.env, CFG_REVIEW_PERIOD_DAYS, 30, int)

    # ---------------------------------------------------------------- guard
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "avg_daily_demand",
            "demand_stddev",
            "history_computed_on",
            "provisional_state",
            "provisional_entered_by_id",
            "provisional_approved_by_id",
            "provisional_approved_on",
            "observed_lead_time_days",
            "lead_time_samples",
            "lead_time_source",
            "safety_stock",
            "reorder_point",
            "target_level",
            "version",
            "previous_id",
            "prepared_by_id",
            "approved_by_id",
            "approved_on",
            "published_on",
            "published_rule_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        rec = self[:1]
        if rec and rec.state != "draft":
            locked |= POLICY_INPUTS
        return locked

    def write(self, vals):
        edited = self.browse()
        stale = self.browse()
        retyped = self.browse()
        if self and not self._fix_guard_open():
            for rec in self:
                if rec.state != "draft":
                    _refuse_frozen(
                        rec,
                        vals,
                        POLICY_INPUTS,
                        "it is %s; revise it to create a new version" % rec.state,
                    )
                    continue
                if _changed(rec, vals, POLICY_INPUTS):
                    edited |= rec
                if _changed(rec, vals, POLICY_HISTORY_KEYS):
                    stale |= rec
                if _changed(rec, vals, PROVISIONAL_INPUTS):
                    retyped |= rec
        res = super().write(vals)
        if edited:
            edited._guarded().write({"prepared_by_id": self.env.user.id})
        if stale:
            stale._guarded().write(
                {
                    "avg_daily_demand": 0.0,
                    "demand_stddev": 0.0,
                    "history_computed_on": False,
                    "observed_lead_time_days": 0.0,
                    "lead_time_samples": 0,
                }
            )
        (retyped | stale.filtered(lambda r: r.provisional_state != "none"))._provisional_entered()
        return res

    def _provisional_entered(self):
        """A typed provisional demand awaits approval; a change voids one given."""
        for rec in self:
            vals = {
                "provisional_state": "entered" if rec.provisional_daily_demand > 0 else "none",
                "provisional_entered_by_id": self.env.user.id,
                "provisional_approved_by_id": False,
                "provisional_approved_on": False,
            }
            if rec.provisional_state == "approved" and not rec.history_computed_on:
                vals.update(avg_daily_demand=0.0, demand_stddev=0.0)
            rec._guarded().write(vals)

    @api.depends("lead_time_days", "observed_lead_time_days", "lead_time_samples")
    def _compute_lead_time_source(self):
        for rec in self:
            rec.lead_time_source = rec._lead_time_source()

    def _lead_time_source(self) -> str:
        if not self.lead_time_samples:
            return "typed"
        if self.lead_time_days == ceil(round(self.observed_lead_time_days, 6)):
            return "observed"
        return "override"

    @api.constrains(
        "lead_time_days",
        "observed_lead_time_days",
        "lead_time_samples",
        "lead_time_override_rationale",
    )
    def _check_lead_time_override(self):
        for rec in self:
            if (
                rec._lead_time_source() == "override"
                and not (rec.lead_time_override_rationale or "").strip()
            ):
                raise ValidationError(
                    "Lead time %d days differs from the %.1f days observed on %d M16 "
                    "receipt(s): record the override rationale."
                    % (rec.lead_time_days, rec.observed_lead_time_days, rec.lead_time_samples)
                )

    @api.constrains("moq_qty", "pack_size", "lead_time_window_days")
    def _check_order_terms(self):
        for rec in self:
            if rec.moq_qty < 0 or rec.pack_size < 0:
                raise ValidationError("MOQ and pack size cannot be negative.")
            if rec.lead_time_window_days < 30 or rec.lead_time_window_days > 1095:
                raise ValidationError("The lead-time window is 30 to 1095 days.")

    # ---------------------------------------------------------------- computes
    @api.depends(
        "avg_daily_demand",
        "demand_stddev",
        "lead_time_days",
        "service_level_pct",
        "review_period_days",
    )
    def _compute_policy(self):
        for rec in self:
            lead = rec.lead_time_days or 0
            rec.safety_stock = safety_stock(rec.service_level_pct, rec.demand_stddev, lead)
            rec.reorder_point = round((rec.avg_daily_demand or 0.0) * lead + rec.safety_stock, 2)
            rec.target_level = round(
                rec.reorder_point + (rec.avg_daily_demand or 0.0) * (rec.review_period_days or 0), 2
            )

    def _segment(self):
        return (
            self.env["fix.demand.segment"]
            .sudo()
            .search([("product_id", "=", self.product_id.id)], limit=1)
        )

    @api.depends("product_id", "part_id")
    def _compute_approval_required(self):
        for rec in self:
            seg = rec._segment()
            rec.approval_required = bool(
                not seg
                or not seg.classified_on
                or seg.abc_class == "a"
                or seg._is_critical()
                or (rec.part_id and rec.part_id.criticality == "critical")
            )

    @api.constrains("part_id", "location_id", "state", "company_id")
    def _check_one_active(self):
        for rec in self.filtered(lambda r: r.state == "active" and r.part_id):
            dup = self.sudo().search_count(
                [
                    ("id", "!=", rec.id),
                    ("company_id", "=", rec.company_id.id),
                    ("part_id", "=", rec.part_id.id),
                    ("location_id", "=", rec.location_id.id),
                    ("state", "=", "active"),
                ]
            )
            if dup:
                raise ValidationError(
                    "%s already has an active policy at %s (one active policy per part and "
                    "location)." % (rec.part_id.display_name, rec.location_id.display_name)
                )

    @api.constrains("history_days", "review_period_days")
    def _check_windows(self):
        for rec in self:
            if rec.history_days < 7 or rec.history_days > 730:
                raise ValidationError("The history window is 7 to 730 days.")
            if rec.review_period_days < 0:
                raise ValidationError("The review period cannot be negative.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.demand.policy") or "DPOL/New"
                )
        records = super().create(vals_list)
        records.filtered(lambda r: r.provisional_daily_demand > 0)._provisional_entered()
        return records

    # ---------------------------------------------------------------- actions
    def action_refresh_from_history(self):
        """Average daily demand and its standard deviation from the M15
        consumption of the last `history_days` days (days without consumption
        count as zero), and the observed lead time from the M16 receipts of
        the last `lead_time_window_days` days (PO sent -> receipt posted). The
        observed lead time (rounded up) becomes the policy's lead time unless
        the planner has recorded an override rationale; with no receipt
        history the typed lead time stays and is labelled typed."""
        require_role(self.env, PLANNER, what="Refreshing policy demand statistics")
        today = fields.Date.today()  # M15 consumed_at is UTC
        for rec in self:
            if rec.state != "draft":
                raise UserError("Refresh a draft policy (revise an active one)")
            if not rec.part_id:
                raise UserError("Policy %s has no M15 spare part to read history for" % rec.name)
            first = today - timedelta(days=rec.history_days)
            daily = consumed_by_day(
                rec.env, rec.company_id, rec.part_id, rec.location_id, first, rec.history_days
            )
            mean, std = mean_and_stddev(daily)
            usable = has_usable_history(rec.env, rec.company_id, rec.part_id, rec.location_id)
            samples = observed_lead_times(
                rec.env,
                rec.company_id,
                rec.product_id,
                today - timedelta(days=rec.lead_time_window_days),
            )
            vals = {
                "avg_daily_demand": round(mean, 4),
                "demand_stddev": round(std, 4),
                "history_computed_on": fields.Datetime.now(),
                "observed_lead_time_days": (
                    round(sum(samples) / len(samples), 2) if samples else 0.0
                ),
                "lead_time_samples": len(samples),
            }
            if samples and not (rec.lead_time_override_rationale or "").strip():
                vals["lead_time_days"] = ceil(round(vals["observed_lead_time_days"], 6))
            if rec.provisional_state == "approved":
                if usable:
                    # real history exists: the manual figure has done its job
                    vals["provisional_state"] = "expired"
                else:
                    for name in ("avg_daily_demand", "demand_stddev", "history_computed_on"):
                        del vals[name]
            rec._guarded().write(vals)
        return True

    def action_approve_provisional(self):
        """BRU-DPL-01: no statistical figure is possible, so a Demand Plan
        Approver who did not enter it lets the manual demand stand, flagged
        provisional, until real history exists."""
        require_role(self.env, APPROVER, what="Approving a provisional demand")
        for rec in self:
            if rec.state != "draft" or rec.provisional_state != "entered":
                raise UserError(
                    "Approve the provisional demand of a draft policy that has one entered "
                    "(policy %s is %s, provisional %s)."
                    % (rec.name, rec.state, rec.provisional_state)
                )
            refuse_self_decision(
                self.env,
                rec.create_uid | rec.prepared_by_id | rec.provisional_entered_by_id,
                "The provisional demand of policy %s" % rec.name,
            )
            if not (rec.provisional_reason or "").strip():
                raise UserError("Policy %s: state why a provisional demand is needed." % rec.name)
            if not rec.part_id:
                raise UserError("Policy %s has no M15 spare part." % rec.name)
            if has_usable_history(self.env, rec.company_id, rec.part_id, rec.location_id):
                raise UserError(
                    "%s has real M15 history: use Refresh from History, not a provisional demand."
                    % rec.part_id.display_name
                )
            rec._guarded().write(
                {
                    "provisional_state": "approved",
                    "provisional_approved_by_id": self.env.user.id,
                    "provisional_approved_on": fields.Datetime.now(),
                    "avg_daily_demand": rec.provisional_daily_demand,
                    "demand_stddev": 0.0,
                }
            )
        return True

    @api.model
    def _cron_expire_provisional(self):
        """Daily: a provisional demand expires once its part has real history.
        The policy stays in force; a plan on it is refused until it is revised."""
        policies = self.sudo().search([("provisional_state", "=", "approved")])
        expired = policies.filtered(
            lambda p: p.part_id
            and has_usable_history(p.env, p.company_id, p.part_id, p.location_id)
        )
        for rec in expired:
            rec._guarded().write({"provisional_state": "expired"})
        return len(expired)

    def _publish_to_m15(self):
        """B1 contract: create or update the M15 reorder rule of the part at the
        location with the computed ROP (min) and target (max)."""
        self.ensure_one()
        Rule = self.env["fix.reorder.rule"]
        kwargs = {}
        # The rule's m43_predicted_demand seam (7-day demand) is passed only
        # if M15's contract accepts it.
        try:
            accepted = inspect.signature(Rule._fix_publish_from_plan).parameters
        except (TypeError, ValueError):
            accepted = {}
        if "predicted_demand" in accepted:
            kwargs["predicted_demand"] = round((self.avg_daily_demand or 0.0) * 7, 3)
        rule = Rule._fix_publish_from_plan(
            self.part_id,
            self.location_id,
            self.reorder_point,
            self.target_level,
            "%s v%d" % (self.name, self.version),
            **kwargs,
        )
        vals = {"published_on": fields.Datetime.now()}
        if isinstance(rule, models.BaseModel) and rule._name == "fix.reorder.rule" and rule:
            vals["published_rule_id"] = rule[:1].id
        self._guarded().write(vals)

    def action_activate(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Activate a draft policy")
            if rec.approval_required:
                require_role(
                    self.env,
                    APPROVER,
                    what="Activating an A-class, critical or unclassified item's policy",
                )
                refuse_self_decision(
                    self.env, rec.create_uid | rec.prepared_by_id, "Policy %s" % rec.name
                )
            else:
                require_role(self.env, PLANNER, APPROVER, what="Activating a policy")
            if not (rec.part_id and rec.location_id):
                raise UserError(
                    "Policy %s needs its M15 spare part and stock location: the reorder rule "
                    "it publishes is per part and location." % rec.name
                )
            if not rec.history_computed_on and rec.provisional_state != "approved":
                raise UserError(
                    "Policy %s has no demand statistics: refresh them from M15 history first, or "
                    "have a provisional demand approved for a part with no history." % rec.name
                )
            if rec.provisional_state == "approved" and has_usable_history(
                self.env, rec.company_id, rec.part_id, rec.location_id
            ):
                raise UserError(
                    "%s now has real M15 history: refresh policy %s from it instead of its "
                    "provisional demand." % (rec.part_id.display_name, rec.name)
                )
            if rec.lead_time_days <= 0:
                raise UserError("Policy %s needs a positive lead time" % rec.name)
            if rec.target_level <= rec.reorder_point:
                raise UserError(
                    "Policy %s has no demand cover above its reorder point (average daily "
                    "demand %.4f, review period %d days): M15 needs a maximum above the "
                    "minimum." % (rec.name, rec.avg_daily_demand, rec.review_period_days)
                )
            others = self.sudo().search(
                [
                    ("id", "!=", rec.id),
                    ("company_id", "=", rec.company_id.id),
                    ("part_id", "=", rec.part_id.id),
                    ("location_id", "=", rec.location_id.id),
                    ("state", "in", ("active", "paused")),
                ]
            )
            if others - rec.previous_id:
                raise UserError(
                    "%s already has a policy in force at %s (%s): revise it instead of "
                    "activating a second one."
                    % (
                        rec.part_id.display_name,
                        rec.location_id.display_name,
                        ", ".join(others.mapped("name")),
                    )
                )
            if rec.previous_id:
                rec.previous_id._guarded().write({"state": "superseded"})
            rec._guarded().write(
                {
                    "state": "active",
                    "approved_by_id": self.env.user.id,
                    "approved_on": fields.Datetime.now(),
                }
            )
            rec._publish_to_m15()
        return True

    def action_revise(self):
        """A parameter change is a new draft version; the version in force
        stays in force until the new one is activated."""
        require_role(self.env, PLANNER, what="Revising a policy")
        self.ensure_one()
        if self.state not in ("active", "paused"):
            raise UserError("Revise an active or paused policy (edit a draft directly)")
        if self.sudo().search_count([("previous_id", "=", self.id), ("state", "=", "draft")]):
            raise UserError("Policy %s already has a draft revision" % self.name)
        new = self.create(
            {
                "product_id": self.product_id.id,
                "part_id": self.part_id.id,
                "location_id": self.location_id.id,
                "company_id": self.company_id.id,
                "history_days": self.history_days,
                "lead_time_days": self.lead_time_days,
                "lead_time_window_days": self.lead_time_window_days,
                "lead_time_override_rationale": self.lead_time_override_rationale,
                "service_level_pct": self.service_level_pct,
                "review_period_days": self.review_period_days,
                "moq_qty": self.moq_qty,
                "pack_size": self.pack_size,
            }
        )
        new._guarded().write({"previous_id": self.id, "version": self.version + 1})
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": new.id,
            "view_mode": "form",
        }

    def action_pause(self):
        require_role(self.env, PLANNER, APPROVER, what="Pausing a policy")
        for rec in self:
            if rec.state != "active":
                raise UserError("Pause an active policy")
            rec._guarded().write({"state": "paused"})
            rec._suspend_m15_rule()
        return True

    def _suspend_m15_rule(self):
        """A paused policy stops replenishing: its published M15 reorder rule
        is archived, which the replenishment sweep skips."""
        self.ensure_one()
        rule = self.published_rule_id.sudo()
        if rule and rule.state != "archived":
            rule._guarded().write({"state": "archived"})

    def action_resume(self):
        for rec in self:
            if rec.state != "paused":
                raise UserError("Resume a paused policy")
            if rec.approval_required:
                require_role(self.env, APPROVER, what="Resuming an A-class or critical policy")
            else:
                require_role(self.env, PLANNER, APPROVER, what="Resuming a policy")
            rec._guarded().write({"state": "active"})
            # publishing restores the archived rule with this version's levels
            rec._publish_to_m15()
        return True


# =====================================================================
# Review cycle
# =====================================================================
class FixDemandReview(models.Model):
    _name = "fix.demand.review"
    _description = "Demand Review Cycle"
    _inherit = ["fix.guarded.mixin"]
    _order = "period desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", index=True, default=lambda self: self.env.company, string="Company"
    )
    period = fields.Char(required=True, help="YYYY-MM")
    owner_id = fields.Many2one("hr.employee", string="Owner")
    due_on = fields.Date(required=True)
    state = fields.Selection(
        [("scheduled", "Scheduled"), ("done", "Done")], required=True, default="scheduled"
    )
    notes = fields.Text(string="Outcome / Notes")
    completed_by_id = fields.Many2one("res.users", string="Completed By", readonly=True)
    completed_on = fields.Datetime(readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "completed_by_id", "completed_on"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        rec = self[:1]
        if rec and rec.state == "done":
            locked |= {"period", "owner_id", "due_on", "notes"}
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.state == "done"):
                _refuse_frozen(
                    rec, vals, {"period", "owner_id", "due_on", "notes"}, "the review is done"
                )
        return super().write(vals)

    @api.constrains("period")
    def _check_period(self):
        for rec in self:
            if not PERIOD_RE.match(rec.period or ""):
                raise ValidationError("Period %r is not a YYYY-MM month." % (rec.period,))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.demand.review") or "DRVW/New"
                )
        return super().create(vals_list)

    def action_complete(self):
        for rec in self:
            if rec.state != "scheduled":
                raise UserError("Complete a scheduled review")
            if not rec.owner_id:
                raise UserError(
                    "Review %s has no owner: assign one before completing it" % rec.name
                )
            if not self.env.su and rec.owner_id.user_id != self.env.user:
                raise UserError(
                    "Review %s is completed by its owner, %s." % (rec.name, rec.owner_id.name)
                )
            if not (rec.notes or "").strip():
                raise UserError("Record the review outcome in the notes before completing it")
            rec._guarded().write(
                {
                    "state": "done",
                    "completed_by_id": self.env.user.id,
                    "completed_on": fields.Datetime.now(),
                }
            )
        return True


# =====================================================================
# Rebalance proposal
# =====================================================================
REBALANCE_INPUTS = {
    "product_id",
    "part_id",
    "source_location_id",
    "target_location_id",
    "qty",
    "transfer_cost",
    "benefit_value",
    "benefit_basis",
    "proposed_on",
    "company_id",
}


class FixDemandRebalance(models.Model):
    _name = "fix.demand.rebalance"
    _description = "Network Rebalance Proposal"
    _inherit = ["fix.guarded.mixin"]
    _order = "proposed_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    product_id = fields.Many2one(
        "product.product", string="Product", required=True, ondelete="restrict", index=True
    )
    part_id = fields.Many2one("fix.spare.part", string="M15 Spare Part", index=True)
    source_location_id = fields.Many2one("fix.stock.location", string="From Location")
    target_location_id = fields.Many2one("fix.stock.location", string="To Location")
    source_branch = fields.Char(
        string="From Branch", compute="_compute_branches", store=True, readonly=True
    )
    target_branch = fields.Char(
        string="To Branch", compute="_compute_branches", store=True, readonly=True
    )
    qty = fields.Float(string="Quantity")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    unit_cost = fields.Monetary(
        string="Unit Cost (M15)",
        currency_field="currency_id",
        compute="_compute_value",
        store=True,
        readonly=True,
    )
    stock_value = fields.Monetary(
        string="Stock Value Moved",
        currency_field="currency_id",
        compute="_compute_value",
        store=True,
        readonly=True,
    )
    transfer_cost = fields.Monetary(string="Estimated Transfer Cost", currency_field="currency_id")
    # BRU-DPL-13: a proposal stands only where the benefit exceeds the transfer
    # cost. The benefit (avoided buy, avoided stockout) is the proposer's estimate
    # with its basis: nothing in M43 computes it yet.
    benefit_value = fields.Monetary(string="Estimated Benefit", currency_field="currency_id")
    benefit_basis = fields.Char(string="Benefit Basis")
    net_benefit = fields.Monetary(
        string="Net Benefit", currency_field="currency_id", compute="_compute_net_benefit"
    )
    source_available = fields.Float(string="Available at Source", compute="_compute_available")
    proposed_on = fields.Date(required=True, default=fields.Date.context_today)
    proposed_by_id = fields.Many2one(
        "res.users", string="Proposed By", default=lambda self: self.env.user, readonly=True
    )
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True)
    decided_on = fields.Datetime(readonly=True)
    transfer_id = fields.Many2one("fix.stock.transfer", string="M15 Transfer", readonly=True)
    state = fields.Selection(
        [("proposed", "Proposed"), ("approved", "Approved"), ("rejected", "Rejected")],
        required=True,
        default="proposed",
    )
    notes = fields.Char()

    _qty_positive = models.Constraint("CHECK (qty > 0)", "Rebalance quantity must be positive")
    _distinct_locations = models.Constraint(
        "CHECK (source_location_id IS NULL OR source_location_id <> target_location_id)",
        "A rebalance moves stock between two different locations",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "unit_cost",
            "stock_value",
            "source_branch",
            "target_branch",
            "source_available",
            "net_benefit",
            "proposed_by_id",
            "decided_by_id",
            "decided_on",
            "transfer_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        rec = self[:1]
        if rec and rec.state != "proposed":
            locked |= REBALANCE_INPUTS | {"notes"}
        return locked

    def write(self, vals):
        edited = self.browse()
        if self and not self._fix_guard_open():
            for rec in self:
                if rec.state != "proposed":
                    _refuse_frozen(rec, vals, REBALANCE_INPUTS, "the proposal is %s" % rec.state)
                elif _changed(rec, vals, REBALANCE_INPUTS):
                    edited |= rec
        res = super().write(vals)
        if edited:
            edited._guarded().write({"proposed_by_id": self.env.user.id})
        return res

    @api.depends("source_location_id", "target_location_id")
    def _compute_branches(self):
        for rec in self:
            src, dst = rec.source_location_id, rec.target_location_id
            rec.source_branch = (src.branch_id.name or src.name) if src else False
            rec.target_branch = (dst.branch_id.name or dst.name) if dst else False

    @api.depends("qty", "part_id", "part_id.unit_cost")
    def _compute_value(self):
        for rec in self:
            rec.unit_cost = rec.part_id.unit_cost if rec.part_id else 0.0
            rec.stock_value = round((rec.qty or 0.0) * rec.unit_cost, 2)

    @api.depends("benefit_value", "transfer_cost")
    def _compute_net_benefit(self):
        for rec in self:
            rec.net_benefit = (rec.benefit_value or 0.0) - (rec.transfer_cost or 0.0)

    @api.depends("part_id", "source_location_id")
    def _compute_available(self):
        for rec in self:
            rec.source_available = (
                on_hand(rec.env, rec.company_id, rec.part_id, rec.source_location_id)
                if rec.part_id and rec.source_location_id
                else 0.0
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.demand.rebalance") or "DRBL/New"
                )
        return super().create(vals_list)

    def action_approve(self):
        """Approval creates the draft M15 transfer; M15 dispatches it."""
        require_role(self.env, APPROVER, what="Approving a rebalance")
        for rec in self:
            if rec.state != "proposed":
                raise UserError("Approve a proposed rebalance")
            refuse_self_decision(
                self.env, rec.create_uid | rec.proposed_by_id, "Rebalance %s" % rec.name
            )
            if not (rec.part_id and rec.source_location_id and rec.target_location_id):
                raise UserError(
                    "Rebalance %s needs the M15 part and both stock locations" % rec.name
                )
            if rec.source_location_id == rec.target_location_id:
                raise UserError("A rebalance moves stock between two different locations")
            if (rec.benefit_value or 0.0) <= (rec.transfer_cost or 0.0):
                raise UserError(
                    "Rebalance %s: the estimated benefit %.2f does not exceed the transfer cost "
                    "%.2f (BRU-DPL-13)." % (rec.name, rec.benefit_value, rec.transfer_cost)
                )
            if not (rec.benefit_basis or "").strip():
                raise UserError("Rebalance %s: state what the benefit is based on." % rec.name)
            if rec.qty > rec.source_available:
                raise UserError(
                    "Rebalance %s moves %.2f but only %.2f is available at %s"
                    % (rec.name, rec.qty, rec.source_available, rec.source_location_id.display_name)
                )
            # The draft transfer is a proposal to M15: its dispatch and receipt
            # stay under M15's own controls.
            transfer = (
                self.env["fix.stock.transfer"]
                .sudo()
                .create(
                    {
                        "company_id": rec.company_id.id,
                        "operating_unit_id": rec.source_location_id.operating_unit_id.id or False,
                        "from_location_id": rec.source_location_id.id,
                        "to_location_id": rec.target_location_id.id,
                        "line_ids": [(0, 0, {"part_id": rec.part_id.id, "qty": rec.qty})],
                    }
                )
            )
            rec._guarded().write(
                {
                    "state": "approved",
                    "decided_by_id": self.env.user.id,
                    "decided_on": fields.Datetime.now(),
                    "transfer_id": transfer.id,
                }
            )
        return True

    def action_reject(self):
        require_role(self.env, APPROVER, what="Rejecting a rebalance")
        for rec in self:
            if rec.state != "proposed":
                raise UserError("Reject a proposed rebalance")
            rec._guarded().write(
                {
                    "state": "rejected",
                    "decided_by_id": self.env.user.id,
                    "decided_on": fields.Datetime.now(),
                }
            )
        return True


# =====================================================================
# What-if scenario
# =====================================================================
SCENARIO_INPUTS = {
    "product_id",
    "policy_id",
    "demand_adjust_pct",
    "lead_time_delta_days",
    "company_id",
}


class FixDemandScenario(models.Model):
    _name = "fix.demand.scenario"
    _description = "What-If Scenario"
    _inherit = ["fix.guarded.mixin"]
    _order = "create_date desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    product_id = fields.Many2one(
        "product.product", string="Product", required=True, ondelete="cascade", index=True
    )
    policy_id = fields.Many2one("fix.demand.policy", string="Base Policy", index=True)
    demand_adjust_pct = fields.Float(string="Demand Adjustment %", default=0.0)
    lead_time_delta_days = fields.Integer(string="Lead Time Delta (days)", default=0)
    base_reorder_point = fields.Float(
        string="Base ROP", compute="_compute_projected", store=True, readonly=True
    )
    projected_lead_time = fields.Integer(
        string="Projected Lead Time", compute="_compute_projected", store=True, readonly=True
    )
    projected_safety_stock = fields.Float(
        string="Projected Safety Stock", compute="_compute_projected", store=True, readonly=True
    )
    projected_reorder_point = fields.Float(
        string="Projected ROP", compute="_compute_projected", store=True, readonly=True
    )
    state = fields.Selection([("draft", "Draft"), ("run", "Run")], required=True, default="draft")
    notes = fields.Char()

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "base_reorder_point",
            "projected_lead_time",
            "projected_safety_stock",
            "projected_reorder_point",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        rec = self[:1]
        if rec and rec.state != "draft":
            locked |= SCENARIO_INPUTS
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.state != "draft"):
                _refuse_frozen(rec, vals, SCENARIO_INPUTS, "the scenario has been run")
        return super().write(vals)

    @api.depends(
        "policy_id",
        "policy_id.avg_daily_demand",
        "policy_id.demand_stddev",
        "policy_id.lead_time_days",
        "policy_id.service_level_pct",
        "policy_id.reorder_point",
        "demand_adjust_pct",
        "lead_time_delta_days",
    )
    def _compute_projected(self):
        """Projected ROP = adjusted daily demand x (lead time + delta) + z x
        adjusted sigma x sqrt(lead time + delta). Demand and its deviation
        scale together (constant coefficient of variation)."""
        for rec in self:
            pol = rec.policy_id
            if not pol:
                rec.base_reorder_point = 0.0
                rec.projected_lead_time = 0
                rec.projected_safety_stock = 0.0
                rec.projected_reorder_point = 0.0
                continue
            factor = 1 + (rec.demand_adjust_pct or 0.0) / 100.0
            lead = max((pol.lead_time_days or 0) + (rec.lead_time_delta_days or 0), 0)
            ss = safety_stock(pol.service_level_pct, (pol.demand_stddev or 0.0) * factor, lead)
            rec.base_reorder_point = pol.reorder_point
            rec.projected_lead_time = lead
            rec.projected_safety_stock = ss
            rec.projected_reorder_point = round(
                (pol.avg_daily_demand or 0.0) * factor * lead + ss, 2
            )

    @api.constrains("policy_id", "product_id")
    def _check_policy_product(self):
        for rec in self:
            if rec.policy_id and rec.policy_id.product_id != rec.product_id:
                raise ValidationError("The scenario's product must be its base policy's product.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.demand.scenario") or "DSCN/New"
                )
            if vals.get("policy_id") and not vals.get("product_id"):
                vals["product_id"] = (
                    self.env["fix.demand.policy"].browse(vals["policy_id"]).product_id.id
                )
        return super().create(vals_list)

    def action_run(self):
        """Running a simulation writes no parameter and no plan (BRU-DPL-15)."""
        require_role(self.env, PLANNER, APPROVER, what="Running a scenario")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Run a draft scenario")
            if not rec.policy_id:
                raise UserError("Scenario %s needs the base policy it varies" % rec.name)
            rec._guarded().write({"state": "run"})
        return True
