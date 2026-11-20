# M43 §5.4 — Replenishment, network & van planning, and §5.3 simulation
# (CD-M43-01). Sub-modules 7 "Planned Orders", 8 "Multi-Echelon
# Rebalancing" and 9 "What-If" capture here.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28
from . import planning_engine as engine
from .fix_demand_history import ABC, CRITICALITY

PLANNED_ORDER_STATES = [
    ("projected", "Projected"),
    ("planned", "Planned"),
    ("consolidated", "Consolidated"),
    ("approved", "Approved"),
    ("released", "Released to M16"),
    ("converted", "Converted"),
    ("closed", "Closed"),
    ("cancelled", "Cancelled"),
]


class FixPlannedOrder(models.Model):
    """FR-DPL-025 / §8.2: proposed supply released to M16 as a draft
    requisition. A and critical parts need a planner (BRU-DPL-08); an
    inactive supplier blocks release (BRU-DPL-11)."""
    _name = "fix.planned.order"
    _description = "Planned Order"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "required_by, id"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(string="Reference", required=True, readonly=True, copy=False,
                       default=lambda self: self.env["ir.sequence"].next_by_code("fix.planned.order") or "New")
    spare_part_id = fields.Many2one("fix.spare.part", string="Spare Part",
                                    required=True, index=True)
    location_id = fields.Many2one("fix.stock.location", string="Destination Location",
                                  required=True, index=True)
    quantity = fields.Float(string="Quantity", required=True, tracking=True)
    required_by = fields.Date(string="Required By", required=True)
    source = fields.Selection([("purchase", "Purchase"), ("transfer", "Transfer"),
                               ("import", "Import")], string="Supply Source",
                              required=True, default="purchase")
    suggested_supplier_id = fields.Many2one("res.partner", string="Suggested Supplier")
    abc_class = fields.Selection(ABC, string="ABC Class", required=True, default="b")
    criticality = fields.Selection(CRITICALITY, string="Criticality", required=True,
                                   default="deferrable")
    parameter_id = fields.Many2one("fix.replenishment.parameter", string="Driving Parameter")
    consolidated_into_id = fields.Many2one("fix.planned.order", string="Consolidated Into",
                                           readonly=True)
    approved_by = fields.Many2one("res.users", string="Approved By", readonly=True)
    requisition_ref = fields.Char(string="M16 Requisition Ref.", readonly=True)
    po_ref = fields.Char(string="M16 Purchase Order Ref.")
    actual_lead_time_days = fields.Float(string="Actual Lead Time (days)")
    cancel_reason = fields.Text(string="Cancellation Reason")
    note_bn = fields.Text(string="মন্তব্য (বাংলা)")
    state = fields.Selection(PLANNED_ORDER_STATES, default="planned", required=True, tracking=True)

    @api.constrains("quantity")
    def _check_quantity(self):
        for rec in self:
            if rec.quantity <= 0:
                raise ValidationError("A planned order needs a positive quantity.")

    def action_approve(self):
        for rec in self:
            if rec.state not in ("planned", "consolidated"):
                raise UserError("Only a planned or consolidated order can be approved.")
            rec.write({"state": "approved", "approved_by": self.env.user.id})

    def action_release(self):
        for rec in self:
            if rec.state != "approved":
                raise UserError("Approve the planned order before releasing it to M16.")
            if rec.source in ("purchase", "import"):
                if not rec.suggested_supplier_id:
                    raise UserError("A purchase or import order needs a supplier before release.")
                if not rec.suggested_supplier_id.active:
                    raise UserError("The supplier is not active — release is blocked (BRU-DPL-11).")
            rec.write({"state": "released", "requisition_ref": rec.name})
            publish(self.env, "demand_plan.planned_order.released", "fix.planned.order",
                    rec.id, {"reference": rec.name,
                             "part": rec.spare_part_id.part_number,
                             "location": rec.location_id.code,
                             "quantity": rec.quantity,
                             "required_by": str(rec.required_by),
                             "source": rec.source,
                             "supplier_id": rec.suggested_supplier_id.id or False})

    def action_mark_converted(self):
        for rec in self:
            if rec.state != "released":
                raise UserError("Only a released order converts to a purchase order.")
            if not rec.po_ref:
                raise UserError("Record the M16 purchase-order reference first.")
            rec.state = "converted"

    def action_close(self):
        for rec in self:
            if rec.state != "converted":
                raise UserError("Only a converted order can be closed on receipt.")
            if not rec.actual_lead_time_days:
                raise UserError("Record the actual lead time — it feeds the lead-time model.")
            rec.state = "closed"
            publish(self.env, "demand_plan.planned_order.closed", "fix.planned.order",
                    rec.id, {"reference": rec.name,
                             "actual_lead_time_days": rec.actual_lead_time_days})

    def action_cancel(self):
        for rec in self:
            if rec.state in ("converted", "closed"):
                raise UserError("Firm supply cannot be cancelled from planning.")
            if not (rec.cancel_reason or "").strip():
                raise UserError("Record why the planned order is cancelled.")
            rec.state = "cancelled"


class FixRebalanceProposal(models.Model):
    """FR-DPL-028 / BRU-DPL-13: surplus at one location covering a shortage
    at another — proposed only where benefit exceeds transfer cost."""
    _name = "fix.rebalance.proposal"
    _description = "Rebalance Proposal"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "net_benefit desc, id desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.company.currency_id)
    spare_part_id = fields.Many2one("fix.spare.part", string="Spare Part",
                                    required=True, index=True)
    from_location_id = fields.Many2one("fix.stock.location", string="From (Surplus)",
                                       required=True)
    to_location_id = fields.Many2one("fix.stock.location", string="To (Shortage)",
                                     required=True)
    quantity = fields.Float(string="Quantity", required=True)
    benefit_value = fields.Monetary(string="Benefit Value", currency_field="currency_id",
                                    help="Avoided stockout cost plus freed excess")
    transfer_cost = fields.Monetary(string="Transfer Cost", currency_field="currency_id")
    net_benefit = fields.Monetary(string="Net Benefit", currency_field="currency_id",
                                  compute="_compute_net", store=True)
    transfer_ref = fields.Char(string="M15 Transfer Ref.", readonly=True)
    rationale_bn = fields.Text(string="যুক্তি (বাংলা)")
    state = fields.Selection([
        ("draft", "Draft"), ("proposed", "Proposed"), ("approved", "Approved"),
        ("transferred", "Transferred"), ("rejected", "Rejected"),
    ], default="draft", required=True, tracking=True)

    @api.depends("benefit_value", "transfer_cost")
    def _compute_net(self):
        for rec in self:
            rec.net_benefit = engine.rebalance_net_benefit(rec.benefit_value, rec.transfer_cost)

    @api.constrains("from_location_id", "to_location_id", "quantity")
    def _check_lanes(self):
        for rec in self:
            if rec.from_location_id == rec.to_location_id:
                raise ValidationError("Source and destination locations must differ.")
            if rec.quantity <= 0:
                raise ValidationError("A transfer needs a positive quantity.")

    def action_propose(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft can be proposed.")
            if rec.net_benefit <= 0:
                raise UserError("The benefit does not exceed the transfer cost — not proposed (BRU-DPL-13).")
            rec.state = "proposed"
            publish(self.env, "demand_plan.rebalance.proposed", "fix.rebalance.proposal",
                    rec.id, {"part": rec.spare_part_id.part_number,
                             "from": rec.from_location_id.code,
                             "to": rec.to_location_id.code,
                             "quantity": rec.quantity,
                             "net_benefit": rec.net_benefit})

    def action_approve(self):
        for rec in self:
            if rec.state != "proposed":
                raise UserError("Only a proposed transfer can be approved.")
            rec.state = "approved"

    def action_mark_transferred(self):
        for rec in self:
            if rec.state != "approved":
                raise UserError("Only an approved transfer can be marked transferred.")
            rec.state = "transferred"

    def action_reject(self):
        self.write({"state": "rejected"})


class FixNetworkPolicy(models.Model):
    """FR-DPL-027: where a part is held — central only, forward at
    branches, or on vans — with the rationale."""
    _name = "fix.network.policy"
    _description = "Network Stocking Policy"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    spare_part_id = fields.Many2one("fix.spare.part", string="Spare Part",
                                    required=True, index=True)
    central_stock = fields.Boolean(string="Stock Centrally", default=True)
    branch_location_ids = fields.Many2many("fix.stock.location",
                                           "fix_network_policy_branch_rel",
                                           "policy_id", "location_id",
                                           string="Forward-Stock Branches")
    van_stock = fields.Boolean(string="Hold on Vans")
    rationale = fields.Text(string="Rationale", required=True)
    rationale_bn = fields.Text(string="যুক্তি (বাংলা)")
    approved_by = fields.Many2one("res.users", string="Approved By", readonly=True)
    state = fields.Selection([("draft", "Draft"), ("approved", "Approved")],
                             default="draft", required=True, tracking=True)

    @api.constrains("central_stock", "branch_location_ids", "van_stock")
    def _check_somewhere(self):
        for rec in self:
            if not (rec.central_stock or rec.branch_location_ids or rec.van_stock):
                # order-on-demand is expressed by policy, not by an empty network
                raise ValidationError("Choose at least one echelon, or set the part's "
                                      "policy to order-on-demand instead.")

    def action_approve(self):
        for rec in self:
            rec.write({"state": "approved", "approved_by": self.env.user.id})
            publish(self.env, "demand_plan.network_policy.approved", "fix.network.policy",
                    rec.id, {"part": rec.spare_part_id.part_number,
                             "central": rec.central_stock,
                             "branches": rec.branch_location_ids.mapped("code"),
                             "van": rec.van_stock})


class FixVanParRecommendation(models.Model):
    """FR-DPL-029 / BRU-DPL-12: van par levels are computed by M43 and
    enforced by M15; applying one needs approval."""
    _name = "fix.van.par.recommendation"
    _description = "Van Par Recommendation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "computed_at desc, id desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    van_location_id = fields.Many2one("fix.stock.location", string="Van",
                                      required=True, domain=[("is_van_location", "=", True)])
    spare_part_id = fields.Many2one("fix.spare.part", string="Spare Part",
                                    required=True, index=True)
    min_qty = fields.Float(string="Par Min", required=True)
    max_qty = fields.Float(string="Par Max", required=True)
    basis = fields.Text(string="Basis (zone consumption, job mix, FTF impact)")
    basis_bn = fields.Text(string="ভিত্তি (বাংলা)")
    computed_at = fields.Datetime(string="Computed At", default=fields.Datetime.now)
    approved_by = fields.Many2one("res.users", string="Approved By", readonly=True)
    applied_at = fields.Datetime(string="Applied to M15 At", readonly=True)
    state = fields.Selection([("draft", "Draft"), ("approved", "Approved"),
                              ("applied", "Applied to M15")],
                             default="draft", required=True, tracking=True)

    @api.constrains("min_qty", "max_qty")
    def _check_par(self):
        for rec in self:
            if rec.min_qty < 0 or rec.max_qty < rec.min_qty:
                raise ValidationError("Par levels need 0 ≤ min ≤ max.")

    def action_approve(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft recommendation can be approved.")
            rec.write({"state": "approved", "approved_by": self.env.user.id})

    def action_apply(self):
        for rec in self:
            if rec.state != "approved":
                raise UserError("Approve the van par level before applying it (BRU-DPL-12).")
            rec.write({"state": "applied", "applied_at": fields.Datetime.now()})
            publish(self.env, "demand_plan.van_par.applied", "fix.van.par.recommendation",
                    rec.id, {"van": rec.van_location_id.code,
                             "part": rec.spare_part_id.part_number,
                             "min": rec.min_qty, "max": rec.max_qty})


class FixPlanningSimulation(models.Model):
    """FR-DPL-024 / T-09 / BRU-DPL-15: a what-if against a snapshot. Running
    it computes numbers on this record only — it never writes parameters or
    planned orders, and publishes no event."""
    _name = "fix.planning.simulation"
    _description = "What-If Simulation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.company.currency_id)
    name = fields.Char(string="Scenario", required=True)
    name_bn = fields.Char(string="দৃশ্যপট (বাংলা)")
    scope = fields.Char(string="Scope (category / location)")
    base_snapshot_ref = fields.Char(string="Base Snapshot Ref.")
    base_service_level = fields.Float(string="Base Service Level (%)", required=True, default=95.0)
    new_service_level = fields.Float(string="Simulated Service Level (%)", required=True, default=98.0)
    demand_change_pct = fields.Float(string="Demand Change (%)")
    lead_time_change_pct = fields.Float(string="Lead-Time Change (%)")
    base_safety_value = fields.Monetary(string="Base Safety-Stock Value", currency_field="currency_id")
    base_cycle_value = fields.Monetary(string="Base Cycle-Stock Value", currency_field="currency_id")
    resulting_investment = fields.Monetary(string="Resulting Investment",
                                           currency_field="currency_id", readonly=True)
    resulting_service_level = fields.Float(string="Resulting Service Level (%)", readonly=True)
    resulting_stockout_risk = fields.Float(string="Stockout Risk (%)", readonly=True)
    run_by = fields.Many2one("res.users", string="Run By", readonly=True)
    run_at = fields.Datetime(string="Run At", readonly=True)
    state = fields.Selection([("draft", "Draft"), ("run", "Run")],
                             default="draft", required=True, tracking=True)

    def action_run(self):
        for rec in self:
            try:
                result = engine.simulate_tradeoff(
                    rec.base_service_level, rec.new_service_level,
                    rec.base_safety_value, rec.base_cycle_value,
                    rec.demand_change_pct, rec.lead_time_change_pct)
            except engine.PlanningError as exc:
                raise UserError(str(exc)) from exc
            result.update({"state": "run", "run_by": self.env.user.id,
                           "run_at": fields.Datetime.now()})
            rec.write(result)

    def action_reset(self):
        self.write({"state": "draft"})
