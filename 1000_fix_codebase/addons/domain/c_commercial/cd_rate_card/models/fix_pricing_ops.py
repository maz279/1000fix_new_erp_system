# M11 pricing operations: price books and versions, price floors, promotions
# and simulation requests. Rate cards, dynamic rules, price explanations and
# discount approvals already live in cd_rate_card / cd_dynamic_pricing.
from odoo import api, fields, models
from odoo.exceptions import UserError


class FixPriceBook(models.Model):
    _name = "fix.price.book"
    _description = "Price Book"
    _order = "name"

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("retired", "Retired")],
        required=True,
        default="draft",
    )
    active = fields.Boolean(default=True)


class FixPriceVersion(models.Model):
    _name = "fix.price.version"
    _description = "Price Book Version"
    _order = "book_id, effective_from desc"

    name = fields.Char(required=True)
    book_id = fields.Many2one("fix.price.book", required=True, ondelete="cascade", index=True)
    version = fields.Char(required=True)
    effective_from = fields.Date(required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("superseded", "Superseded")],
        required=True,
        default="draft",
    )
    approved_by = fields.Many2one("res.users", readonly=True)
    note = fields.Char()


class FixPriceFloor(models.Model):
    _name = "fix.price.floor"
    _description = "Price Floor"
    _inherit = ["fix.dofa.mixin"]
    _order = "name"

    # A below-floor sale is a concession, so it carries the same authority the
    # rest of the estate uses: the tier follows the size of the discount, the
    # approver must hold it, and the person who raised it cannot clear it.
    # The first implementation stamped env.user with no check at all
    # (A04 audit, 2026-10-31).
    _DOFA_DISCOUNT_THRESHOLDS = [
        (15.0, "tier_2"),  # up to 15% below floor
        (30.0, "tier_3"),  # up to 30% below floor
        (float("inf"), "tier_4"),
    ]

    # A11 audit P2 (A04 area): the override used to be cleared by whoever
    # pressed Approve while holding the tier — no request, no named approver,
    # no deadline, no delegate, no history. It is now a routed M63 request:
    # the raiser asks (action_request_override_approval), the engine routes to
    # the holders of the tier the shortfall derives (minus the raiser and the
    # amount-changer), and the flags are stamped from the approver's inbox
    # only. The shortfall percentage is the approval amount, so moving the
    # floor or the proposed price while the request is pending withdraws it.
    _approval_domain = "price_floor_override"
    _approval_apply_method = "action_approve_dofa_override"
    _approval_routed = True

    name = fields.Char(required=True)
    product_code = fields.Char(required=True, index=True)
    catalogue_item_id = fields.Many2one("fix.catalogue.item", string="Catalogue Item")
    book_id = fields.Many2one("fix.price.book", string="Price Book")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    floor_price = fields.Monetary(required=True)
    active = fields.Boolean(default=True)

    # DOFA Floor Governance & Delegation of Financial Authority (FLAW-11.2)
    dofa_tier = fields.Selection(
        [
            ("tier1", "Tier 1 - Commercial Director (<15% below floor)"),
            ("tier2", "Tier 2 - Managing Director (<30% below floor)"),
            ("tier3", "Tier 3 - Board of Directors (>=30% below floor)"),
        ],
        string="Required DOFA Tier for Floor Override",
        default="tier1",
        required=True,
    )
    dofa_override_approved = fields.Boolean(
        string="DOFA Override Approved", default=False, readonly=True
    )
    dofa_override_user_id = fields.Many2one("res.users", string="DOFA Approver", readonly=True)

    proposed_override_price = fields.Monetary(
        string="Proposed Below-Floor Price",
        help="The price the override is being sought for. The DOFA tier is "
        "derived from how far below the floor it sits.",
    )

    def _dofa_amount(self) -> float:
        """Percentage below floor — the measure the tier is derived from."""
        self.ensure_one()
        if not self.floor_price or not self.proposed_override_price:
            return 0.0
        shortfall = self.floor_price - self.proposed_override_price
        if shortfall <= 0:
            return 0.0
        return (shortfall / self.floor_price) * 100.0

    def _dofa_thresholds(self):
        return self._DOFA_DISCOUNT_THRESHOLDS

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "a price %.1f%% below the floor for '%s'" % (
            self._dofa_amount(),
            self.product_code,
        )

    @api.depends("floor_price", "proposed_override_price")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def action_request_override_approval(self, justification=None):
        """A11 audit P2: route the below-floor override through M63 — the
        holders of the tier the shortfall derives decide it from their inbox."""
        for rec in self:
            if not rec.proposed_override_price:
                raise UserError(
                    "Record the proposed below-floor price before seeking an "
                    "override: the approval tier is derived from how far below "
                    "the floor it sits."
                )
            rec.action_request_approval(justification=justification)

    def action_approve_dofa_override(self):
        """Approve a below-floor price under real DOFA authority — from the
        approver's M63 inbox only (a direct press is refused)."""
        for rec in self:
            if not rec.proposed_override_price:
                raise UserError(
                    "Record the proposed below-floor price before seeking an "
                    "override: the approval tier is derived from how far below "
                    "the floor it sits."
                )
            rec.action_dofa_approve()
            rec._guarded().write(
                {
                    "dofa_override_approved": True,
                    "dofa_override_user_id": rec.dofa_approved_by.id,
                }
            )

    def _fix_guarded_fields(self) -> set:
        # The override stamps change only through the approve action.
        return super()._fix_guarded_fields() | {"dofa_override_approved", "dofa_override_user_id"}

    def validate_price_against_floor(self, proposed_price: float):
        """Statutory guard blocking transaction pricing below floor without DOFA approval."""
        self.ensure_one()
        # An override only covers the price it was granted for.
        if (
            proposed_price < self.floor_price
            and self.dofa_override_approved
            and self.proposed_override_price
            and proposed_price < self.proposed_override_price
        ):
            raise UserError(
                "Proposed price %.2f BDT is below the %.2f BDT the DOFA "
                "override was granted for on '%s'. Re-approval is required."
                % (proposed_price, self.proposed_override_price, self.product_code)
            )
        if proposed_price < self.floor_price and not self.dofa_override_approved:
            raise UserError(
                "Proposed price %.2f BDT is strictly below statutory price floor %.2f BDT for '%s'. "
                "DOFA Commercial Director override approval is mandatory before proceeding."
                % (proposed_price, self.floor_price, self.product_code)
            )
        return True


class FixPromotion(models.Model):
    _name = "fix.promotion"
    _description = "Promotion"
    _order = "name"

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    discount_type = fields.Selection(
        [("percent", "Percentage"), ("fixed", "Fixed amount")],
        required=True,
        default="percent",
    )
    value = fields.Float(required=True)
    channel = fields.Selection(
        [
            ("all", "All channels"),
            ("portal", "Customer portal"),
            ("branch", "Branch"),
            ("corporate", "Corporate"),
        ],
        required=True,
        default="all",
    )
    valid_from = fields.Date()
    valid_until = fields.Date()
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("ended", "Ended")],
        required=True,
        default="draft",
    )
    active = fields.Boolean(default=True)


class FixDiscountPolicy(models.Model):
    """Who may give how much discount without escalation."""

    _name = "fix.discount.policy"
    _description = "Discount Policy"
    _order = "min_pct"

    name = fields.Char(required=True)
    role = fields.Selection(
        [
            ("agent", "Service Agent"),
            ("supervisor", "Supervisor"),
            ("manager", "Manager"),
            ("director", "Director"),
        ],
        required=True,
        default="agent",
    )
    min_pct = fields.Float(required=True, default=0.0, help="Band start (inclusive).")
    max_pct = fields.Float(required=True, default=5.0, help="Band end (inclusive).")
    requires_approval = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    active = fields.Boolean(default=True)


class FixPriceSimulation(models.Model):
    _name = "fix.price.simulation"
    _description = "Price Simulation Request"
    _order = "create_date desc, id desc"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    catalogue_item_id = fields.Many2one("fix.catalogue.item", string="Catalogue Item")
    rate_card_id = fields.Many2one("fix.rate.card", string="Rate Card")
    input_json = fields.Text(help="Scenario inputs (quantity, channel, discount…).")
    result_json = fields.Text(readonly=True, help="Computed output — filled by the pricing engine.")
    state = fields.Selection(
        [("draft", "Draft"), ("computed", "Computed")], required=True, default="draft"
    )
    requested_by = fields.Many2one("res.users", default=lambda self: self.env.user, readonly=True)
    computed_at = fields.Datetime(readonly=True)


class FixApprovalMatrixFloorDomains(models.Model):
    """A11 audit P2: lets a DoA matrix row target the routed price-floor
    override (SLA, escalation, policy) without touching any other DOFA
    approval."""

    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[("price_floor_override", "Price-Floor Override")],
        ondelete={"price_floor_override": "cascade"},
    )
