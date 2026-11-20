# M43 §5.1 — Demand history, quality & segmentation (CD-M43-01).
# Sub-modules 1 "History & Cleansing" and 2 "Segmentation" capture here.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28
from . import planning_engine as engine

DEMAND_STREAMS = [
    ("routine_repair", "Routine Repair"),
    ("warranty_campaign", "Warranty Campaign"),
    ("contract_amc", "Contract / AMC"),
    ("project_rollout", "Project Roll-out"),
    ("rental_fleet", "Rental Fleet"),
    ("refurbishment", "Refurbishment"),
]
ABC = [("a", "A"), ("b", "B"), ("c", "C")]
XYZ = [("x", "X"), ("y", "Y"), ("z", "Z")]
CRITICALITY = [
    ("job_stopping", "Job-Stopping"),
    ("deferrable", "Deferrable"),
    ("cosmetic", "Cosmetic"),
]


class FixDemandAdjustment(models.Model):
    """FR-DPL-003/004, T-01: an overlay on the consumption history — the
    source series is never edited; every outlier, censored-demand or
    reclassification decision is recorded with its reason and actor."""
    _name = "fix.demand.adjustment"
    _description = "Demand History Adjustment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "period desc, id desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    spare_part_id = fields.Many2one("fix.spare.part", string="Spare Part",
                                    required=True, index=True)
    location_id = fields.Many2one("fix.stock.location", string="Stock Location",
                                  required=True, index=True)
    demand_stream = fields.Selection(DEMAND_STREAMS, string="Demand Stream",
                                     required=True, default="routine_repair")
    period = fields.Date(string="Period", required=True)
    adjustment_type = fields.Selection([
        ("outlier", "Outlier Treatment"),
        ("censored", "Censored-Demand Correction"),
        ("reclassified", "Stream Reclassification"),
    ], string="Adjustment Type", required=True, default="outlier")
    treatment = fields.Selection([
        ("include", "Include"),
        ("exclude", "Exclude"),
        ("replace", "Replace Value"),
        ("reclassify", "Move to Another Stream"),
    ], string="Treatment", required=True, default="replace")
    target_stream = fields.Selection(DEMAND_STREAMS, string="Reclassify To")
    original_value = fields.Float(string="Original Quantity", required=True)
    adjusted_value = fields.Float(string="Adjusted Quantity")
    reason = fields.Text(string="Reason", required=True)
    reason_bn = fields.Text(string="কারণ (বাংলা)")
    actor_id = fields.Many2one("res.users", string="Planner",
                               default=lambda self: self.env.user, readonly=True)
    applied_at = fields.Datetime(string="Applied At", readonly=True)
    state = fields.Selection([
        ("draft", "Draft"),
        ("applied", "Applied"),
        ("cancelled", "Cancelled"),
    ], default="draft", required=True, tracking=True)

    @api.constrains("treatment", "target_stream", "demand_stream")
    def _check_reclassification(self):
        for rec in self:
            if rec.treatment == "reclassify":
                if not rec.target_stream:
                    raise ValidationError("A reclassification needs the target demand stream.")
                if rec.target_stream == rec.demand_stream:
                    raise ValidationError("The target stream must differ from the current one (BRU-DPL-05).")

    def action_apply(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft adjustment can be applied.")
            if not (rec.reason or "").strip():
                raise UserError("Every history adjustment needs a recorded reason (FR-DPL-003).")
            rec.write({"state": "applied", "applied_at": fields.Datetime.now()})
            publish(self.env, "demand_plan.history.adjusted", "fix.demand.adjustment",
                    rec.id, {"part": rec.spare_part_id.part_number,
                             "location": rec.location_id.code,
                             "type": rec.adjustment_type,
                             "original": rec.original_value,
                             "adjusted": rec.adjusted_value})

    def action_cancel(self):
        self.write({"state": "cancelled"})


class FixPartSegment(models.Model):
    """FR-DPL-006..009: the nine-box plus criticality, intermittency and
    lifecycle per part (network or location scope). Intermittency and the
    forecasting method are COMPUTED from ADI/CV² — the planner captures the
    inputs and the business classifications, never the method by hand
    (BRU-DPL-04)."""
    _name = "fix.part.segment"
    _description = "Part Segment Classification"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "computed_at desc, id desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.company.currency_id)
    spare_part_id = fields.Many2one("fix.spare.part", string="Spare Part",
                                    required=True, index=True)
    scope = fields.Selection([("network", "Network"), ("location", "Location")],
                             string="Scope", required=True, default="network")
    location_id = fields.Many2one("fix.stock.location", string="Stock Location")
    consumption_value_12m = fields.Monetary(string="12-Month Consumption Value",
                                            currency_field="currency_id")
    abc_class = fields.Selection(ABC, string="ABC Class", required=True, default="c")
    xyz_class = fields.Selection(XYZ, string="XYZ Class", required=True, default="z")
    nine_box = fields.Char(string="Nine-Box Cell", compute="_compute_nine_box", store=True)
    criticality = fields.Selection(CRITICALITY, string="Criticality",
                                   required=True, default="deferrable")
    adi = fields.Float(string="Avg. Inter-Demand Interval (ADI)", default=1.0)
    cv_squared = fields.Float(string="CV² of Demand Size", default=0.0)
    intermittency_class = fields.Selection([
        ("smooth", "Smooth"), ("erratic", "Erratic"),
        ("intermittent", "Intermittent"), ("lumpy", "Lumpy"),
    ], string="Demand Pattern", compute="_compute_pattern", store=True)
    forecast_method = fields.Selection([
        ("ets", "Exponential Smoothing (ETS)"),
        ("croston_sba", "Croston / SBA"),
        ("bootstrap", "Lead-Time Demand Bootstrap"),
    ], string="Forecast Method", compute="_compute_pattern", store=True)
    lifecycle_stage = fields.Selection([
        ("new", "New"), ("growth", "Growth"), ("mature", "Mature"),
        ("declining", "Declining"), ("end_of_life", "End of Life"),
    ], string="Lifecycle Stage", default="mature")
    default_policy = fields.Selection([
        ("continuous_rop", "Continuous Reorder Point"),
        ("order_on_demand", "No Stock / Order on Demand"),
    ], string="Default Policy", compute="_compute_nine_box", store=True)
    computed_at = fields.Datetime(string="Classified At", default=fields.Datetime.now)
    state = fields.Selection([("draft", "Draft"), ("published", "Published")],
                             default="draft", required=True, tracking=True)

    @api.depends("abc_class", "xyz_class", "criticality")
    def _compute_nine_box(self):
        for rec in self:
            rec.nine_box = engine.nine_box(rec.abc_class, rec.xyz_class) if rec.abc_class and rec.xyz_class else False
            rec.default_policy = engine.default_policy(rec.abc_class, rec.xyz_class, rec.criticality)

    @api.depends("adi", "cv_squared", "criticality")
    def _compute_pattern(self):
        for rec in self:
            if rec.adi and rec.adi > 0 and rec.cv_squared >= 0:
                pattern = engine.classify_intermittency(rec.adi, rec.cv_squared)
                rec.intermittency_class = pattern
                rec.forecast_method = engine.method_for(pattern, rec.criticality == "job_stopping")
            else:
                rec.intermittency_class = False
                rec.forecast_method = False

    @api.constrains("scope", "location_id")
    def _check_scope(self):
        for rec in self:
            if rec.scope == "location" and not rec.location_id:
                raise ValidationError("A location-scope segment needs its stock location.")

    def action_publish(self):
        """Publish the classification for M15 counting and M41 slotting."""
        for rec in self:
            rec.state = "published"
            publish(self.env, "demand_plan.segment.published", "fix.part.segment",
                    rec.id, {"part": rec.spare_part_id.part_number,
                             "nine_box": rec.nine_box,
                             "criticality": rec.criticality,
                             "pattern": rec.intermittency_class})
