# fix_demand_plan — M43: demand planning and replenishment (P09-M07).
#
# A06 audit (2026-11-03):
#  - M43-3/M43-4: the plan's forecast, stock and reorder point were typed and
#    the recommended order compared a shortfall with a stock level. Every
#    figure is now computed: demand from the approved forecasts of the plan
#    months, stock from M15 owned on-hand at the plan location, on-order from
#    M16, ROP / safety stock / target from the active policy; the order is
#    "at or below ROP -> up to target, net of stock on order" (S8).
#  - M43-2: approval by a Demand Plan Approver who neither created nor changed
#    the plan, from env.user; the approved figures are pinned (a change of an
#    input voids the approval) and the requisition uses the pinned quantity.
#  - M43-1/M43-5/M43-12: the plan releases a DRAFT requisition submitted into
#    M16's own approval, priced and attributed to the planner's employee, and
#    a plan can never produce a second requisition.
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish

from .fix_demand_common import (
    APPROVER,
    CFG_ENFORCE_BUDGET,
    PLANNER,
    apply_moq_pack,
    budget_headroom,
    has_usable_history,
    months_between,
    on_hand,
    on_order,
    order_up_to,
    param,
    refuse_self_decision,
    require_role,
)

# what the approval covered: changing one of these voids it
PLAN_PINNED = {
    "product_id",
    "part_id",
    "location_id",
    "period_start",
    "period_end",
    "operating_unit_id",
    "company_id",
    "vendor_id",
}
# a plan in these states has reached M16: its figures are history
PLAN_RELEASED_STATES = ("released", "converted", "closed")
PLAN_POSITION = (
    "policy_id",
    "forecast_quantity",
    "forecast_months_covered",
    "current_stock",
    "on_order_qty",
    "safety_stock",
    "reorder_point",
    "target_level",
    "projected_stock",
    "raw_order_qty",
    "recommended_order",
)
PLAN_SNAPSHOT = (
    "approved_forecast",
    "approved_stock",
    "approved_on_order",
    "approved_reorder_point",
    "approved_target_level",
    "approved_order_qty",
)


class FixDemandPlan(models.Model):
    """Demand planning on M15's reorder seam: the approved forecast and the
    active policy feed the replenishment recommendation."""

    _name = "fix.demand.plan"
    _description = "Demand Plan"
    _inherit = ["fix.guarded.mixin", "mail.thread", "mail.activity.mixin"]
    _order = "period_start desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    period_start = fields.Date(required=True)
    period_end = fields.Date(required=True)
    product_id = fields.Many2one(
        "product.template", string="Product", required=True, help="What M16 buys"
    )
    part_id = fields.Many2one(
        "fix.spare.part", string="M15 Spare Part", index=True, help="What M15 stocks and consumes"
    )
    location_id = fields.Many2one(
        "fix.stock.location", string="Stock Location", index=True, help="Planning scope"
    )
    vendor_id = fields.Many2one(
        "res.partner",
        string="Supplier",
        help="The supplier of this planned order. Empty = the last purchase order's supplier. "
        "It must be active in M42 before release (BRU-DPL-11).",
    )

    # ---- the computed position (never typed)
    policy_id = fields.Many2one(
        "fix.demand.policy", string="Active Policy", compute="_compute_position"
    )
    forecast_quantity = fields.Float(
        string="Forecast Demand",
        compute="_compute_position",
        help="Sum of the approved / published forecasts of the plan months",
    )
    forecast_months_covered = fields.Char(string="Forecast Months", compute="_compute_position")
    current_stock = fields.Float(
        string="Current Stock", compute="_compute_position", help="M15 owned available on-hand"
    )
    on_order_qty = fields.Float(string="On Order", compute="_compute_position")
    safety_stock = fields.Float(string="Safety Stock", compute="_compute_position")
    reorder_point = fields.Float(string="Reorder Point", compute="_compute_position")
    target_level = fields.Float(string="Target (Max) Level", compute="_compute_position")
    projected_stock = fields.Float(
        string="Projected Stock",
        compute="_compute_position",
        help="Stock + on order - forecast demand of the period",
    )
    raw_order_qty = fields.Float(
        compute="_compute_position",
        string="Order Before MOQ / Pack",
        help="Up to the target level, before the policy's MOQ and pack-size rounding",
    )
    recommended_order = fields.Float(
        compute="_compute_position",
        string="Recommended Order Qty",
        help="The order up to target, at least the MOQ and in whole packs",
    )
    budget_check = fields.Char(string="Budget Check", readonly=True, copy=False)

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("approved", "Approved"),
            ("released", "Released to M16"),
            ("converted", "Converted to PO"),
            ("closed", "Closed (received)"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    prepared_by_id = fields.Many2one(
        "res.users",
        string="Prepared By",
        default=lambda self: self.env.user,
        readonly=True,
        copy=False,
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True, copy=False)
    approved_on = fields.Datetime(readonly=True, copy=False)
    approved_forecast = fields.Float(readonly=True, copy=False)
    approved_stock = fields.Float(readonly=True, copy=False)
    approved_on_order = fields.Float(readonly=True, copy=False)
    approved_reorder_point = fields.Float(readonly=True, copy=False)
    approved_target_level = fields.Float(readonly=True, copy=False)
    approved_order_qty = fields.Float(string="Approved Order Qty", readonly=True, copy=False)
    pr_requisition_id = fields.Many2one(
        "fix.requisition", string="Purchase Requisition", readonly=True, copy=False
    )
    pr_state = fields.Selection(
        related="pr_requisition_id.state", string="Requisition State", readonly=True
    )
    purchase_order_id = fields.Many2one(
        "fix.purchase.order", string="Purchase Order", readonly=True, copy=False, index=True
    )
    actual_lead_time_days = fields.Integer(
        string="Actual Lead Time (days)",
        readonly=True,
        copy=False,
        help="From the plan's approval to the PO being fully received.",
    )

    _period_order = models.Constraint(
        "CHECK (period_end >= period_start)", "A plan period cannot end before it starts"
    )

    # ------------------------------------------------------------ guard
    def _fix_guarded_fields(self) -> set:
        return (
            super()._fix_guarded_fields()
            | {
                "state",
                "prepared_by_id",
                "approved_by_id",
                "approved_on",
                "pr_requisition_id",
                "purchase_order_id",
                "actual_lead_time_days",
                "budget_check",
            }
            | set(PLAN_POSITION)
            | set(PLAN_SNAPSHOT)
        )

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        rec = self[:1]
        if rec and rec.state in PLAN_RELEASED_STATES:
            locked |= PLAN_PINNED | {"name"}
        return locked

    def write(self, vals):
        void = self.browse()
        if self and not self._fix_guard_open():
            pinned = PLAN_PINNED & set(vals)
            for rec in self:
                changed = [n for n in pinned if rec._fix_guard_differs(n, vals[n], rec[n])]
                if not changed:
                    continue
                if rec.state in PLAN_RELEASED_STATES:
                    raise UserError(
                        "Plan %s is released to M16 (requisition %s); its figures cannot change."
                        % (rec.name, rec.pr_requisition_id.display_name)
                    )
                void |= rec
        approved = void.filtered(lambda r: r.state == "approved")
        res = super().write(vals)
        if void:
            # whoever changes what the approval covers becomes a preparer, and
            # an approval already given is void
            void._guarded().write({"prepared_by_id": self.env.user.id})
        if approved:
            approved._guarded().write(
                {
                    "state": "draft",
                    "approved_by_id": False,
                    "approved_on": False,
                    **dict.fromkeys(PLAN_SNAPSHOT, 0.0),
                }
            )
            for rec in approved:
                rec.message_post(body="Approval void: a planned input changed after approval.")
        return res

    # ------------------------------------------------------------ position
    def _position(self) -> dict:
        self.ensure_one()
        out = dict.fromkeys(PLAN_POSITION, 0.0)
        out.update(policy_id=False, forecast_months_covered="")
        if not (self.part_id and self.location_id and self.period_start and self.period_end):
            return out
        company = self.company_id or self.env.company
        policy = (
            self.env["fix.demand.policy"]
            .sudo()
            .search(
                [
                    ("company_id", "=", company.id),
                    ("part_id", "=", self.part_id.id),
                    ("location_id", "=", self.location_id.id),
                    ("state", "=", "active"),
                ],
                limit=1,
            )
        )
        months = months_between(self.period_start, self.period_end)
        forecasts = (
            self.env["fix.demand.forecast"]
            .sudo()
            .search(
                [
                    ("company_id", "=", company.id),
                    ("part_id", "=", self.part_id.id),
                    ("location_id", "=", self.location_id.id),
                    ("period", "in", months),
                    ("state", "in", ("approved", "published")),
                ]
            )
        )
        demand = round(sum(forecasts.mapped("forecast_qty")), 3)
        stock = on_hand(self.env, company, self.part_id, self.location_id)
        incoming = on_order(self.env, company, self.product_id.product_variant_ids)
        projected = round(stock + incoming - demand, 3)
        raw = order_up_to(projected, policy.reorder_point, policy.target_level) if policy else 0.0
        out.update(
            policy_id=policy.id,
            forecast_quantity=demand,
            forecast_months_covered=", ".join(sorted(set(forecasts.mapped("period")))),
            current_stock=stock,
            on_order_qty=incoming,
            safety_stock=policy.safety_stock,
            reorder_point=policy.reorder_point,
            target_level=policy.target_level,
            projected_stock=projected,
            raw_order_qty=raw,
            recommended_order=apply_moq_pack(raw, policy.moq_qty, policy.pack_size),
        )
        return out

    @api.depends("part_id", "location_id", "period_start", "period_end", "product_id", "company_id")
    def _compute_position(self):
        for rec in self:
            rec.update(rec._position())

    def _preparers(self):
        return self.create_uid | self.prepared_by_id

    # ------------------------------------------------------------ approval
    def action_approve(self):
        require_role(self.env, APPROVER, what="Approving a demand plan")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Approve a draft plan (plan %s is %s)" % (rec.name, rec.state))
            refuse_self_decision(self.env, rec._preparers(), "Demand plan %s" % rec.name)
            if not (rec.part_id and rec.location_id):
                raise UserError(
                    "Plan %s needs its M15 spare part and stock location: the stock position "
                    "and the policy are read from them." % rec.name
                )
            pos = rec._position()
            if not pos["policy_id"]:
                raise UserError(
                    "Plan %s has no active replenishment policy for %s at %s."
                    % (rec.name, rec.part_id.display_name, rec.location_id.display_name)
                )
            policy = self.env["fix.demand.policy"].sudo().browse(pos["policy_id"])
            if policy.provisional_state == "expired" or (
                policy.provisional_state == "approved"
                and has_usable_history(self.env, rec.company_id, rec.part_id, rec.location_id)
            ):
                raise UserError(
                    "Policy %s runs on a provisional demand and %s now has real M15 history: "
                    "revise the policy from history before approving plan %s."
                    % (policy.name, rec.part_id.display_name, rec.name)
                )
            months = months_between(rec.period_start, rec.period_end)
            covered = set(filter(None, pos["forecast_months_covered"].split(", ")))
            missing = [m for m in months if m not in covered]
            if missing:
                raise UserError(
                    "Plan %s has no approved forecast for %s." % (rec.name, ", ".join(missing))
                )
            if pos["recommended_order"] <= 0:
                raise UserError(
                    "Nothing to replenish — the projected stock %.2f is above the reorder "
                    "point %.2f" % (pos["projected_stock"], pos["reorder_point"])
                )
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.user.id,
                    "approved_on": fields.Datetime.now(),
                    "approved_forecast": pos["forecast_quantity"],
                    "approved_stock": pos["current_stock"],
                    "approved_on_order": pos["on_order_qty"],
                    "approved_reorder_point": pos["reorder_point"],
                    "approved_target_level": pos["target_level"],
                    "approved_order_qty": pos["recommended_order"],
                }
            )
            publish(
                self.env,
                "demand_plan.approved",
                "fix.demand.plan",
                rec.id,
                {"product": rec.product_id.name, "quantity": pos["recommended_order"]},
            )

    # ------------------------------------------------------------ M16 release
    def _pr_price_and_vendor(self, product):
        """Unit price and supplier for the requisition: the last purchase-order
        price for the product, else its standard cost; the plan's supplier,
        else the last purchase order's."""
        line = (
            self.env["fix.purchase.order.line"]
            .sudo()
            .search(
                [
                    ("product_id", "=", product.id),
                    ("order_id.company_id", "=", self.company_id.id),
                    ("order_id.state", "!=", "cancelled"),
                    ("unit_price", ">", 0),
                ],
                order="id desc",
                limit=1,
            )
        )
        price = line.unit_price if line else (product.standard_price or 0.0)
        vendor = self.vendor_id or (line.order_id.vendor_id if line else self.env["res.partner"])
        return price, vendor

    def _refuse_unsourced(self, vendor):
        """BRU-DPL-11: a planned order is not released without a supplier that
        is active in M42."""
        self.ensure_one()
        if not vendor:
            raise UserError(
                "Plan %s cannot be released: it names no supplier and %s has no purchase history "
                "to take one from (BRU-DPL-11)." % (self.name, self.product_id.display_name)
            )
        if "fix.supplier" not in self.env:
            return
        partners = vendor | vendor.commercial_partner_id
        if not (
            self.env["fix.supplier"]
            .sudo()
            .search_count([("partner_id", "in", partners.ids), ("status", "=", "active")])
        ):
            raise UserError(
                "Plan %s cannot be released: %s is not an active supplier in M42 (BRU-DPL-11)."
                % (self.name, vendor.display_name)
            )

    def action_generate_pr(self):
        """Release the approved quantity to M16 as a DRAFT requisition and
        submit it into M16's own approval (never born approved)."""
        require_role(self.env, PLANNER, APPROVER, what="Releasing a planned order to M16")
        Requisition = self.env["fix.requisition"]
        for plan in self:
            if plan.pr_requisition_id or Requisition.sudo().search_count(
                [("demand_plan_id", "=", plan.id)]
            ):
                raise UserError("Plan %s already has a requisition" % plan.name)
            if plan.state != "approved":
                raise UserError("Approve the plan before generating a requisition")
            qty = plan.approved_order_qty
            if qty <= 0:
                raise UserError("Nothing to order — the plan has no approved quantity")
            if not plan.part_id:
                raise UserError("Plan %s has no M15 spare part: the order is unsourced" % plan.name)
            product = plan.product_id.product_variant_id
            if not product:
                raise UserError("Plan %s has no purchasable product variant" % plan.name)
            price, vendor = plan._pr_price_and_vendor(product)
            if price <= 0:
                raise UserError(
                    "Plan %s cannot be released: %s has no purchase price or standard cost, "
                    "so the requisition would carry no value for M16's authority check."
                    % (plan.name, product.display_name)
                )
            plan._refuse_unsourced(vendor)
            employee = self.env.user.employee_id
            if not employee:
                raise UserError(
                    "Your user has no employee record: a requisition is requested by an employee."
                )
            ou = (
                plan.operating_unit_id
                or self.env.user.default_operating_unit_id
                or self.env["operating.unit"].search(
                    [("company_id", "=", plan.company_id.id)], limit=1
                )
            )
            if not ou:
                raise UserError("Plan %s has no operating unit for its requisition" % plan.name)
            estimate = round(qty * price, 2)
            # M43-5 budget check (report only unless cd_demand_plan.enforce_budget = 1)
            remaining, budget_note = budget_headroom(self.env, plan.company_id, fields.Date.today())
            if remaining is not None and estimate > remaining:
                budget_note = "Over budget: BDT %.2f requisition against BDT %.2f remaining. %s" % (
                    estimate,
                    remaining,
                    budget_note,
                )
                if param(self.env, CFG_ENFORCE_BUDGET, 0, int):
                    raise UserError("Plan %s cannot be released. %s" % (plan.name, budget_note))
            vals = {
                "description": "Planned order — %s (%s)" % (plan.product_id.name, plan.name),
                "product_id": product.id,
                "qty": qty,
                "estimate_amount": estimate,
                "urgency": "normal",
                "requested_by": employee.id,
                "operating_unit_id": ou.id,
                "company_id": plan.company_id.id,
                "demand_plan_id": plan.id,
                "vendor_id": vendor.id,
            }
            requisition = Requisition.create(vals)
            plan._guarded().write(
                {
                    "pr_requisition_id": requisition.id,
                    "state": "released",
                    "budget_check": budget_note,
                }
            )
            # B2 contract: M16's own submission routes the approval
            requisition.action_submit()
            plan.message_post(
                body="Released to M16 as requisition %s (%s units, BDT %.2f), submitted for "
                "approval. %s" % (requisition.display_name, qty, estimate, budget_note)
            )
        return True

    def action_reopen(self, reason=None):
        """M16 refused the planned order (requisition rejected or cancelled, or
        its PO cancelled): the plan returns to draft, to be approved again and
        reissued. The dead requisition keeps its history and stops counting
        as this plan's requisition."""
        require_role(self.env, PLANNER, APPROVER, what="Reopening a planned order")
        for plan in self:
            req = plan.pr_requisition_id.sudo()
            order = plan.purchase_order_id.sudo()
            dead = req.state in ("rejected", "cancelled") or order.state == "cancelled"
            if plan.state not in ("released", "converted") or not dead:
                raise UserError(
                    "Plan %s can be reopened only when M16 has rejected or cancelled its "
                    "requisition or cancelled its purchase order." % plan.name
                )
            why = (reason or "").strip()
            if not why:
                raise UserError("State why plan %s is reopened." % plan.name)
            req.write({"demand_plan_id": False, "reissued_from_plan_id": plan.id})
            plan.sudo()._guarded().write(
                {
                    "state": "draft",
                    "pr_requisition_id": False,
                    "purchase_order_id": False,
                    "budget_check": False,
                    "approved_by_id": False,
                    "approved_on": False,
                    "prepared_by_id": self.env.user.id,
                    **dict.fromkeys(PLAN_SNAPSHOT, 0.0),
                }
            )
            plan.sudo().message_post(
                body="Reopened by %s after requisition %s was %s: %s"
                % (self.env.user.name, req.display_name, req.state, why)
            )
        return True

    def _plan_sync_from_po(self, order):
        """Converted -> Closed once the PO is fully received, with the actual
        lead time written back."""
        for plan in self.sudo().filtered(lambda p: p.state == "converted"):
            received = order.received_on or fields.Date.context_today(plan)
            days = (received - plan.approved_on.date()).days if plan.approved_on else 0
            plan._guarded().write({"state": "closed", "actual_lead_time_days": max(days, 0)})


class FixRequisitionDemandLink(models.Model):
    """M43-12: the requisition knows the plan that raised it; one per plan
    (DB unique), and the link is set at creation only. M43 step 12: the
    conversion moves the plan on, read here so cd_requisition stays untouched."""

    _inherit = "fix.requisition"

    demand_plan_id = fields.Many2one(
        "fix.demand.plan", string="Source Demand Plan", readonly=True, copy=False, index=True
    )
    reissued_from_plan_id = fields.Many2one(
        "fix.demand.plan",
        string="Plan Reissued After This Requisition",
        readonly=True,
        copy=False,
        index=True,
    )

    _demand_plan_unique = models.Constraint(
        "UNIQUE (demand_plan_id)", "A demand plan raises at most one requisition"
    )

    def write(self, vals):
        if "demand_plan_id" in vals and not self.env.su:
            for rec in self:
                if (rec.demand_plan_id.id or False) != (vals["demand_plan_id"] or False):
                    raise UserError(
                        "The source demand plan of a requisition is set when M43 raises it "
                        "and cannot be changed."
                    )
        res = super().write(vals)
        if vals.get("state") == "converted":
            for req in self.sudo().filtered("demand_plan_id"):
                if req.demand_plan_id.state == "released":
                    req.demand_plan_id._guarded().write(
                        {"state": "converted", "purchase_order_id": req.purchase_order_id.id}
                    )
        return res


class FixPurchaseOrderDemandLink(models.Model):
    _inherit = "fix.purchase.order"

    def write(self, vals):
        res = super().write(vals)
        if vals.get("state") == "received":
            Plan = self.env["fix.demand.plan"].sudo()
            for order in self.sudo():
                Plan.search([("purchase_order_id", "=", order.id)])._plan_sync_from_po(order)
        return res
