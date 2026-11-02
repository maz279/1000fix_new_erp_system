# M35 Marketing operations: journeys, behaviour triggers, offers, creative
# assets, portal ads and experiments. Campaigns and responses already live in
# fix.campaign / fix.campaign.response.
from odoo import api, fields, models


class FixCampaignJourney(models.Model):
    _name = "fix.campaign.journey"
    _description = "Marketing Journey"
    _order = "name"

    name = fields.Char(required=True)
    campaign_id = fields.Many2one("fix.campaign", required=True, ondelete="cascade", index=True)
    trigger_event = fields.Char(help="The event that starts the journey (e.g. order.closed).")
    steps_json = fields.Text(help="Ordered multi-step definition as JSON.")
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("paused", "Paused")],
        required=True,
        default="draft",
    )
    active = fields.Boolean(default=True)


# Which outbox event type each friendly trigger label listens for.
#
# The four original labels named nothing the estate actually publishes, which
# is part of why no trigger ever fired. They are kept (screens and data use
# them) and each now resolves to an event type; the four that have no producer
# yet are marked so, because a trigger that waits for an event nobody emits
# should say so rather than look configured.
TRIGGER_OUTBOX_EVENTS = {
    "order_closed": "service_order.closed",
    "survey_low": "survey.detractor_flagged",
    "cart_abandon": "storefront.cart_abandoned",
    "inactivity": "party.inactivity_detected",
    "party_role_added": "party.role_added",
    "loyalty_tier_upgraded": "loyalty.tier_upgraded",
    "consent_captured": "consent.captured",
}

# Event types that no module publishes yet. A trigger bound to one of these
# is inert, and saying so on the record is better than a marketer waiting for
# a journey that cannot start.
TRIGGER_EVENTS_WITHOUT_PRODUCER = {
    "service_order.closed",
    "storefront.cart_abandoned",
    "party.inactivity_detected",
}


class FixCampaignTrigger(models.Model):
    _name = "fix.campaign.trigger"
    _description = "Behaviour Trigger"
    _order = "name"

    name = fields.Char(required=True)
    campaign_id = fields.Many2one("fix.campaign", required=True, ondelete="cascade", index=True)
    event = fields.Selection(
        [
            ("order_closed", "Service order closed"),
            ("survey_low", "Low survey rating"),
            ("cart_abandon", "Cart abandoned"),
            ("inactivity", "Customer inactivity"),
            ("party_role_added", "Party role added"),
            ("loyalty_tier_upgraded", "Loyalty tier upgraded"),
            ("consent_captured", "Consent captured"),
        ],
        required=True,
        default="order_closed",
    )
    outbox_event_type = fields.Char(
        string="Outbox Event Type",
        compute="_compute_outbox_event_type",
        store=True,
        readonly=False,
        help="The dot-notation event this trigger listens for. Defaulted from "
        "the label above and editable, because the estate's event names are "
        "the contract, not this list.",
    )
    producer_missing = fields.Boolean(
        string="No Producer Yet",
        compute="_compute_outbox_event_type",
        store=True,
        help="True when nothing in the estate publishes this event, so the "
        "trigger cannot fire. Shown rather than hidden.",
    )
    delay_hours = fields.Integer(required=True, default=0)
    active = fields.Boolean(default=True)

    @api.depends("event")
    def _compute_outbox_event_type(self):
        for rec in self:
            if not rec.outbox_event_type or rec._origin.event != rec.event:
                rec.outbox_event_type = TRIGGER_OUTBOX_EVENTS.get(rec.event, "")
            rec.producer_missing = rec.outbox_event_type in TRIGGER_EVENTS_WITHOUT_PRODUCER


class FixCampaignOffer(models.Model):
    _name = "fix.campaign.offer"
    _description = "Marketing Offer"
    _order = "name"

    name = fields.Char(required=True)
    name_bn = fields.Char(
        string="Offer Name (Bengali)",
        help="DE-17: the offer wording a Bengali-speaking recipient reads.",
    )
    campaign_id = fields.Many2one("fix.campaign", required=True, ondelete="cascade", index=True)
    offer_type = fields.Selection(
        [
            ("percent", "Percentage discount"),
            ("fixed", "Fixed amount off"),
            ("gift", "Gift / bundle"),
        ],
        required=True,
        default="percent",
    )
    value = fields.Float(help="Percent value or fixed BDT amount (0 for gifts).")
    valid_from = fields.Date()
    valid_until = fields.Date()
    active = fields.Boolean(default=True)

    # FLAW-35.3 & HS-08: Promo code exploitation & budget overspend controls
    promo_code = fields.Char(
        string="Promo Code",
        index=True,
        help="Customer-facing voucher or promotional code (e.g. FIXSUMMER26)",
    )
    max_redemptions_per_customer = fields.Integer(
        string="Max Redemptions Per Customer",
        default=1,
        help="Prevent repeated multi-account redemption abuse",
    )
    total_budget_cap_bdt = fields.Monetary(
        string="Total Budget Cap (BDT)",
        currency_field="currency_id",
        help="Hard cap on total promotional discount value across all redemptions",
    )
    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        default=lambda self: self.env.ref("base.BDT"),
    )
    total_redeemed_bdt = fields.Monetary(
        string="Total Redeemed (BDT)",
        currency_field="currency_id",
        readonly=True,
        default=0.0,
    )
    redemption_count = fields.Integer(
        string="Redemption Count",
        readonly=True,
        default=0,
    )

    def validate_customer_eligibility(self, partner_id, order_subtotal_bdt=0.0):
        """Validate if customer is eligible to apply this offer on an order.
        Returns dict with status, discount amount, and reason message (HS-08)."""
        self.ensure_one()
        today = fields.Date.context_today(self)

        if not self.active:
            return {"eligible": False, "discount_bdt": 0.0, "reason": "Offer is inactive"}
        if self.campaign_id.state != "running":
            return {
                "eligible": False,
                "discount_bdt": 0.0,
                "reason": "Associated campaign is not running",
            }
        if self.valid_from and today < self.valid_from:
            return {"eligible": False, "discount_bdt": 0.0, "reason": "Offer has not started yet"}
        if self.valid_until and today > self.valid_until:
            return {"eligible": False, "discount_bdt": 0.0, "reason": "Offer has expired"}

        # Check total budget cap
        if self.total_budget_cap_bdt > 0 and self.total_redeemed_bdt >= self.total_budget_cap_bdt:
            return {
                "eligible": False,
                "discount_bdt": 0.0,
                "reason": "Campaign promotional budget ceiling reached",
            }

        # Check partner redemption limit
        partner = self.env["res.partner"].browse(partner_id) if partner_id else None
        if partner:
            prior_redemptions = self.env["fix.campaign.response"].search_count(
                [
                    ("campaign_id", "=", self.campaign_id.id),
                    ("partner_id", "=", partner.id),
                    ("conversion_status", "in", ("converted", "enrolled_loyalty")),
                ]
            )
            if (
                self.max_redemptions_per_customer > 0
                and prior_redemptions >= self.max_redemptions_per_customer
            ):
                return {
                    "eligible": False,
                    "discount_bdt": 0.0,
                    "reason": f"Maximum redemption limit ({self.max_redemptions_per_customer}) reached for this customer",
                }

        # Calculate discount
        discount_bdt = 0.0
        if self.offer_type == "percent":
            discount_bdt = round(order_subtotal_bdt * (self.value / 100.0), 2)
        elif self.offer_type == "fixed":
            discount_bdt = min(self.value, order_subtotal_bdt)

        # Cap discount to remaining budget if budget cap is set
        if self.total_budget_cap_bdt > 0:
            remaining_budget = max(0.0, self.total_budget_cap_bdt - self.total_redeemed_bdt)
            discount_bdt = min(discount_bdt, remaining_budget)

        return {
            "eligible": True,
            "discount_bdt": discount_bdt,
            "reason": "Offer validated successfully",
        }

    def action_record_redemption(self, partner_id, discount_applied_bdt):
        """Record an offer redemption against this offer and its campaign."""
        self.ensure_one()
        self.sudo().write(
            {
                "total_redeemed_bdt": self.total_redeemed_bdt + discount_applied_bdt,
                "redemption_count": self.redemption_count + 1,
            }
        )
        self.env["fix.campaign.response"].sudo().create(
            {
                "campaign_id": self.campaign_id.id,
                "partner_id": partner_id,
                "response_type": "service_booking",
                "conversion_status": "converted",
            }
        )


class FixCampaignCreative(models.Model):
    _name = "fix.campaign.creative"
    _description = "Marketing Creative Asset"
    _order = "name"

    name = fields.Char(required=True)
    campaign_id = fields.Many2one("fix.campaign", required=True, ondelete="cascade", index=True)
    asset_type = fields.Selection(
        [("image", "Image"), ("video", "Video"), ("copy", "Copy"), ("landing", "Landing page")],
        required=True,
        default="image",
    )
    channel = fields.Char()
    reference = fields.Char(help="Exact asset reference (S3 key / URL) — never a fabricated path.")
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("retired", "Retired")],
        required=True,
        default="draft",
    )


class FixCampaignAd(models.Model):
    _name = "fix.campaign.ad"
    _description = "Portal Ad Placement"
    _order = "name"

    name = fields.Char(required=True)
    campaign_id = fields.Many2one("fix.campaign", required=True, ondelete="cascade", index=True)
    placement = fields.Selection(
        [
            ("portal_home", "Customer portal home"),
            ("checkout", "Checkout"),
            ("tracking", "Order tracking"),
        ],
        required=True,
        default="portal_home",
    )
    active = fields.Boolean(default=True)
    impressions = fields.Integer(readonly=True, default=0)
    clicks = fields.Integer(readonly=True, default=0)


class FixCampaignExperiment(models.Model):
    _name = "fix.campaign.experiment"
    _description = "Marketing A/B Experiment"
    _order = "name"

    name = fields.Char(required=True)
    campaign_id = fields.Many2one("fix.campaign", required=True, ondelete="cascade", index=True)
    variant_a_pct = fields.Integer(
        required=True, default=50, help="Share of the audience in variant A."
    )
    metric = fields.Selection(
        [
            ("response", "Response rate"),
            ("conversion", "Conversion rate"),
            ("revenue", "Attributed revenue"),
        ],
        required=True,
        default="response",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("running", "Running"), ("concluded", "Concluded")],
        required=True,
        default="draft",
    )
    result_note = fields.Char()


class FixDndRegistry(models.Model):
    """The BTRC national Do-Not-Disturb registry, mirrored locally.

    REQ-35.1 requires every promotional audience to be scrubbed against the
    national DND list within 24 hours of launch. Before the A03 zero-trust
    audit (2026-10-31) no such list existed anywhere in the estate: the
    workspace relabelled PDPA consent counts as "DND", which is a different
    control answering a different law.

    Rows are loaded by the telco aggregator adapter. An empty registry is a
    legitimate state (nothing to exclude); what launch verifies is that the
    scrub was performed and is recent, not that it found anything.
    """

    _name = "fix.dnd.registry"
    _description = "BTRC Do-Not-Disturb Registry"
    _order = "msisdn"
    _rec_name = "msisdn"
    _msisdn_unique = models.Constraint(
        "UNIQUE (msisdn)", "A subscriber appears on the DND registry once."
    )

    msisdn = fields.Char(
        string="Subscriber Number",
        required=True,
        index=True,
        help="Mobile number in the form stored on res.partner (e.g. 01711123456).",
    )
    source = fields.Selection(
        [
            ("btrc_feed", "BTRC National Feed"),
            ("operator", "Mobile Operator Feed"),
            ("customer_request", "Direct Customer Opt-Out"),
        ],
        required=True,
        default="btrc_feed",
    )
    registered_on = fields.Date(
        string="Listed On", default=fields.Date.context_today, required=True
    )
    active = fields.Boolean(default=True)
