# M43 §5.3 — Inventory policy & parameters (CD-M43-01).
# Sub-modules 5 "Safety Stock & ROP" and 6 "Lead-Time" capture here.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28
from . import planning_engine as engine
from .fix_demand_history import ABC, CRITICALITY

LOCATION_TYPES = [
    ("central", "Central Warehouse"),
    ("branch", "Branch"),
    ("van", "Van"),
]


class FixServiceLevelTarget(models.Model):
    """FR-DPL-018: target service level by segment, criticality and location
    type — e.g. 98% for A-class job-stopping parts at central."""
    _name = "fix.service.level.target"
    _description = "Service-Level Target"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "effective_from desc, id desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(string="Target", compute="_compute_name", store=True)
    name_bn = fields.Char(string="লক্ষ্য (বাংলা)")
    abc_class = fields.Selection(ABC, string="ABC Class", required=True, default="a")
    criticality = fields.Selection(CRITICALITY, string="Criticality", required=True,
                                   default="job_stopping")
    location_type = fields.Selection(LOCATION_TYPES, string="Location Type",
                                     required=True, default="central")
    target_cycle_service = fields.Float(string="Cycle Service Target (%)", required=True,
                                        default=95.0, tracking=True)
    target_fill_rate = fields.Float(string="Fill-Rate Target (%)", default=98.0)
    z_value = fields.Float(string="Safety Factor (z)", compute="_compute_z", store=True,
                           digits=(6, 3))
    set_by = fields.Many2one("res.users", string="Set By",
                             default=lambda self: self.env.user, readonly=True)
    effective_from = fields.Date(string="Effective From", required=True,
                                 default=fields.Date.context_today)
    active = fields.Boolean(default=True)

    @api.depends("abc_class", "criticality", "location_type", "target_cycle_service")
    def _compute_name(self):
        for rec in self:
            rec.name = (f"{(rec.abc_class or '').upper()} · {rec.criticality or ''} · "
                        f"{rec.location_type or ''} → {rec.target_cycle_service:g}%")

    @api.depends("target_cycle_service")
    def _compute_z(self):
        for rec in self:
            try:
                rec.z_value = engine.z_for_service_level(rec.target_cycle_service)
            except engine.PlanningError:
                rec.z_value = 0.0

    @api.constrains("target_cycle_service", "target_fill_rate")
    def _check_targets(self):
        for rec in self:
            if not 50.0 <= rec.target_cycle_service < 100.0:
                raise ValidationError("The cycle-service target must be at least 50% and below 100%.")
            if rec.target_fill_rate and not 0.0 < rec.target_fill_rate <= 100.0:
                raise ValidationError("The fill-rate target must be between 0% and 100%.")


class FixLeadTimeModel(models.Model):
    """FR-DPL-019 / BRU-DPL-09: lead time per part per supplier from ACTUAL
    receipts; the quoted figure is kept only for comparison."""
    _name = "fix.lead.time.model"
    _description = "Lead-Time Profile"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "last_updated desc, id desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    spare_part_id = fields.Many2one("fix.spare.part", string="Spare Part",
                                    required=True, index=True)
    supplier_id = fields.Many2one("res.partner", string="Supplier", required=True, index=True)
    source = fields.Selection([("domestic", "Domestic"), ("import", "Import")],
                              string="Supply Source", required=True, default="domestic")
    quoted_days = fields.Float(string="Supplier-Quoted Lead Time (days)")
    observation_ids = fields.One2many("fix.lead.time.observation", "model_id",
                                      string="Actual Receipts")
    sample_count = fields.Integer(string="Samples", compute="_compute_stats", store=True)
    mean_days = fields.Float(string="Mean Actual (days)", compute="_compute_stats", store=True)
    std_dev_days = fields.Float(string="Std. Deviation (days)", compute="_compute_stats", store=True)
    p95_days = fields.Float(string="P95 (days)", compute="_compute_stats", store=True)
    quote_variance_days = fields.Float(string="Actual − Quoted (days)",
                                       compute="_compute_stats", store=True)
    last_updated = fields.Datetime(string="Last Updated", compute="_compute_stats", store=True)
    notes_bn = fields.Text(string="মন্তব্য (বাংলা)")

    _part_supplier_source_unique = models.Constraint(
        "UNIQUE (company_id, spare_part_id, supplier_id, source)",
        "One lead-time profile per part, supplier and supply source.")

    @api.depends("observation_ids.lead_days", "quoted_days")
    def _compute_stats(self):
        for rec in self:
            stats = engine.lead_time_statistics(rec.observation_ids.mapped("lead_days"))
            rec.sample_count = stats["sample_count"]
            rec.mean_days = stats["mean_days"]
            rec.std_dev_days = stats["std_dev_days"]
            rec.p95_days = stats["p95_days"]
            rec.quote_variance_days = (stats["mean_days"] - rec.quoted_days
                                       if stats["sample_count"] and rec.quoted_days else 0.0)
            rec.last_updated = fields.Datetime.now()


class FixLeadTimeObservation(models.Model):
    """One actual receipt feeding a lead-time profile (line of its parent)."""
    _name = "fix.lead.time.observation"
    _description = "Lead-Time Observation"
    _order = "received_on desc, id desc"

    model_id = fields.Many2one("fix.lead.time.model", string="Lead-Time Profile",
                               required=True, ondelete="cascade", index=True)
    order_ref = fields.Char(string="PO / Consignment Ref.", required=True)
    ordered_on = fields.Date(string="Ordered On", required=True)
    received_on = fields.Date(string="Received On", required=True)
    lead_days = fields.Float(string="Lead Time (days)", compute="_compute_days", store=True)

    @api.depends("ordered_on", "received_on")
    def _compute_days(self):
        for rec in self:
            rec.lead_days = ((rec.received_on - rec.ordered_on).days
                             if rec.ordered_on and rec.received_on else 0.0)

    @api.constrains("ordered_on", "received_on")
    def _check_dates(self):
        for rec in self:
            if rec.received_on < rec.ordered_on:
                raise ValidationError("A receipt cannot precede its order.")


class FixReplenishmentParameter(models.Model):
    """FR-DPL-020..023: the versioned parameter set M15 executes against
    (prototype form "Policy Assignment"). Safety stock and ROP are computed
    from variability and the service target — never typed in (BRU-DPL-07)."""
    _name = "fix.replenishment.parameter"
    _description = "Policy Assignment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "effective_from desc, version desc, id desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    spare_part_id = fields.Many2one("fix.spare.part", string="Spare Part",
                                    required=True, index=True)
    location_id = fields.Many2one("fix.stock.location", string="Stock Location",
                                  required=True, index=True)
    version = fields.Integer(string="Version", default=1, readonly=True)
    policy_type = fields.Selection([
        ("continuous_rop", "Continuous Reorder Point"),
        ("periodic_review", "Periodic Review"),
        ("min_max", "Min-Max"),
        ("order_on_demand", "No Stock / Order on Demand"),
    ], string="Policy", required=True, default="continuous_rop", tracking=True)
    abc_class = fields.Selection(ABC, string="ABC Class", required=True, default="b")
    criticality = fields.Selection(CRITICALITY, string="Criticality", required=True,
                                   default="deferrable")
    service_level_target_id = fields.Many2one("fix.service.level.target",
                                              string="Service-Level Target", required=True)
    lead_time_model_id = fields.Many2one("fix.lead.time.model", string="Lead-Time Profile")
    mean_daily_demand = fields.Float(string="Mean Daily Demand", required=True)
    std_daily_demand = fields.Float(string="Daily Demand Std. Dev.", required=True)
    mean_lead_days = fields.Float(string="Mean Lead Time (days)", required=True)
    std_lead_days = fields.Float(string="Lead-Time Std. Dev. (days)")
    review_period_days = fields.Integer(string="Review Period (days)", default=7)
    annual_order_cost = fields.Float(string="Cost per Order (BDT)")
    unit_holding_cost = fields.Float(string="Annual Holding Cost per Unit (BDT)")
    supplier_moq = fields.Float(string="Supplier MOQ")
    pack_size = fields.Float(string="Pack Size")
    safety_stock = fields.Float(string="Safety Stock", compute="_compute_parameters", store=True)
    reorder_point = fields.Float(string="Reorder Point", compute="_compute_parameters", store=True)
    eoq = fields.Float(string="Economic Order Qty", compute="_compute_parameters", store=True)
    reorder_qty = fields.Float(string="Reorder Qty", compute="_compute_parameters", store=True)
    min_qty = fields.Float(string="Min Qty", compute="_compute_parameters", store=True)
    max_qty = fields.Float(string="Max Qty", compute="_compute_parameters", store=True)
    constraints_applied = fields.Text(string="Constraints Applied", compute="_compute_parameters",
                                      store=True)
    provisional = fields.Boolean(string="Provisional (readiness failed)",
                                 help="BRU-DPL-01: set when the history failed the readiness gate")
    needs_review = fields.Boolean(string="Planner Review Required", readonly=True)
    approved_by = fields.Many2one("res.users", string="Approved By", readonly=True)
    effective_from = fields.Date(string="Effective From", required=True,
                                 default=fields.Date.context_today)
    effective_to = fields.Date(string="Effective To", readonly=True)
    rationale_bn = fields.Text(string="যুক্তি (বাংলা)")
    state = fields.Selection([
        ("draft", "Draft"),
        ("pending_review", "Pending Planner Review"),
        ("approved", "Approved"),
        ("published", "Published to M15"),
        ("superseded", "Superseded"),
    ], default="draft", required=True, tracking=True)

    @api.depends("service_level_target_id.target_cycle_service", "mean_daily_demand",
                 "std_daily_demand", "mean_lead_days", "std_lead_days", "review_period_days",
                 "annual_order_cost", "unit_holding_cost", "supplier_moq", "pack_size", "policy_type")
    def _compute_parameters(self):
        for rec in self:
            target = rec.service_level_target_id.target_cycle_service
            if rec.policy_type == "order_on_demand" or not target:
                rec.update({"safety_stock": 0.0, "reorder_point": 0.0, "eoq": 0.0,
                            "reorder_qty": 0.0, "min_qty": 0.0, "max_qty": 0.0,
                            "constraints_applied": False})
                continue
            exposure = rec.mean_lead_days + (rec.review_period_days
                                             if rec.policy_type == "periodic_review" else 0)
            try:
                ss = engine.safety_stock(target, rec.mean_daily_demand, rec.std_daily_demand,
                                         exposure, rec.std_lead_days or 0.0)
            except engine.PlanningError:
                # invalid inputs: _check_inputs reports them on save
                rec.update({"safety_stock": 0.0, "reorder_point": 0.0, "eoq": 0.0,
                            "reorder_qty": 0.0, "min_qty": 0.0, "max_qty": 0.0,
                            "constraints_applied": False})
                continue
            rop = engine.reorder_point(rec.mean_daily_demand, exposure, ss)
            eoq = engine.economic_order_quantity(rec.mean_daily_demand * 365.0,
                                                 rec.annual_order_cost, rec.unit_holding_cost)
            base_qty = eoq or rec.mean_daily_demand * max(rec.review_period_days, 1)
            qty, notes = engine.apply_order_constraints(base_qty, rec.supplier_moq, rec.pack_size)
            rec.update({"safety_stock": ss, "reorder_point": rop, "eoq": eoq,
                        "reorder_qty": qty, "min_qty": rop, "max_qty": round(rop + qty, 2),
                        "constraints_applied": "\n".join(notes) or False})

    @api.constrains("mean_daily_demand", "std_daily_demand", "mean_lead_days",
                    "std_lead_days", "review_period_days", "supplier_moq", "pack_size")
    def _check_inputs(self):
        for rec in self:
            if min(rec.mean_daily_demand, rec.std_daily_demand, rec.mean_lead_days,
                   rec.std_lead_days, rec.review_period_days, rec.supplier_moq, rec.pack_size) < 0:
                raise ValidationError("Demand, lead-time and order-constraint inputs cannot be negative.")

    def _previous_published(self):
        self.ensure_one()
        return self.search([
            ("company_id", "=", self.company_id.id),
            ("spare_part_id", "=", self.spare_part_id.id),
            ("location_id", "=", self.location_id.id),
            ("state", "=", "published"),
            ("id", "!=", self.id),
        ], order="version desc", limit=1)

    def action_submit(self):
        """BRU-DPL-08 / T-13: A-class and job-stopping always need a planner;
        B/C auto-approve only inside the guard rail."""
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft parameter set can be submitted.")
            prev = rec._previous_published()
            rec.version = (prev.version + 1) if prev else 1
            review = engine.requires_planner_review(rec.abc_class, rec.criticality,
                                                    prev.reorder_point if prev else 0.0,
                                                    rec.reorder_point)
            rec.needs_review = review
            if review:
                rec.state = "pending_review"
            else:
                rec.write({"state": "approved", "approved_by": self.env.user.id})

    def action_approve(self):
        for rec in self:
            if rec.state != "pending_review":
                raise UserError("Only a parameter set pending review can be approved.")
            rec.write({"state": "approved", "approved_by": self.env.user.id})

    def action_reject(self):
        for rec in self:
            if rec.state != "pending_review":
                raise UserError("Only a parameter set pending review can be sent back.")
            rec.state = "draft"

    def action_publish(self):
        """Publish to M15; the prior version is superseded, never overwritten
        (T-05, BRU-DPL-18)."""
        for rec in self:
            if rec.state != "approved":
                raise UserError("Only an approved parameter set can be published.")
            prev = rec._previous_published()
            if prev:
                prev.write({"state": "superseded", "effective_to": rec.effective_from})
            rec.state = "published"
            publish(self.env, "demand_plan.parameter.published", "fix.replenishment.parameter",
                    rec.id, {"part": rec.spare_part_id.part_number,
                             "location": rec.location_id.code,
                             "version": rec.version, "policy": rec.policy_type,
                             "safety_stock": rec.safety_stock,
                             "reorder_point": rec.reorder_point,
                             "min_qty": rec.min_qty, "max_qty": rec.max_qty,
                             "provisional": rec.provisional})
