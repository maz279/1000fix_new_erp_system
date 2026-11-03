# M35 Marketing operations: journeys, behaviour triggers, offers, creative
# assets, portal ads and experiments. Campaigns and responses already live in
# fix.campaign / fix.campaign.response.
from odoo import api, fields, models
from odoo.exceptions import UserError


class FixCampaignJourney(models.Model):
    _name = "fix.campaign.journey"
    _description = "Marketing Journey"
    _inherit = ["fix.guarded.mixin"]
    _order = "name"

    def _fix_guarded_fields(self) -> set:
        # A journey's state decides whether it sends. Writing state='active'
        # outran the campaign's launch gates, and writing it back to 'active'
        # under a paused campaign re-opened sending (A03 audit G-M35-5).
        return super()._fix_guarded_fields() | {"state", "launched_at", "paused_by_campaign"}

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
    paused_by_campaign = fields.Boolean(
        string="Paused With Its Campaign",
        readonly=True,
        copy=False,
        help="Set when pausing the campaign paused this journey, so resuming "
        "the campaign resumes exactly these journeys and not ones a marketer "
        "paused on purpose.",
    )


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

# The R8 consumer every trigger event is delivered to (A03 audit G-M35-8).
JOURNEY_CONSUMER_MODEL = "fix.campaign.journey"
JOURNEY_CONSUMER_METHOD = "consume_journey_trigger"


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

    consumer_registered = fields.Boolean(
        string="Listening",
        compute="_compute_consumer_registered",
        help="True when the event relay (R8) delivers this event type to the "
        "journey engine. Without it a trigger journey never enrols anybody.",
    )

    @api.depends("event")
    def _compute_outbox_event_type(self):
        for rec in self:
            if not rec.outbox_event_type or rec._origin.event != rec.event:
                rec.outbox_event_type = TRIGGER_OUTBOX_EVENTS.get(rec.event, "")
            rec.producer_missing = rec.outbox_event_type in TRIGGER_EVENTS_WITHOUT_PRODUCER

    @api.depends("outbox_event_type")
    def _compute_consumer_registered(self):
        Consumer = self.env["fix.event.consumer"].sudo()
        for rec in self:
            rec.consumer_registered = bool(
                rec.outbox_event_type
                and Consumer.search_count(
                    [
                        ("event_type", "=", rec.outbox_event_type),
                        ("model", "=", JOURNEY_CONSUMER_MODEL),
                        ("method", "=", JOURNEY_CONSUMER_METHOD),
                        ("active", "=", True),
                    ]
                )
            )

    def _ensure_event_consumer(self):
        """Register the journey engine as an R8 consumer of this trigger's event.

        A03 audit G-M35-8: enrol_from_event had no caller, so trigger journeys
        never admitted a member. The seven labelled event types are registered
        as data (data/fix_journey_consumers.xml); an edited, custom event type
        is registered here. The consumer's model and method are fixed by this
        code, never taken from the record, so a marketer can choose only WHICH
        event wakes the journey engine.
        """
        Consumer = self.env["fix.event.consumer"].sudo()
        for rec in self.filtered("outbox_event_type"):
            domain = [
                ("event_type", "=", rec.outbox_event_type),
                ("model", "=", JOURNEY_CONSUMER_MODEL),
                ("method", "=", JOURNEY_CONSUMER_METHOD),
            ]
            if not Consumer.with_context(active_test=False).search_count(domain):
                Consumer.create(
                    {
                        "name": "M35 journeys: enrol on %s" % rec.outbox_event_type,
                        "event_type": rec.outbox_event_type,
                        "model": JOURNEY_CONSUMER_MODEL,
                        "method": JOURNEY_CONSUMER_METHOD,
                        "module": "cd_campaign",
                    }
                )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._ensure_event_consumer()
        return records

    def write(self, vals):
        result = super().write(vals)
        if "outbox_event_type" in vals or "event" in vals:
            self._ensure_event_consumer()
        return result


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


# The content of a creative: what the approver looked at. An approved
# creative must be withdrawn before any of these changes (SFMC content
# approval, A03 audit G-M35-10).
CREATIVE_CONTENT_FIELDS = frozenset({"name", "campaign_id", "asset_type", "channel", "reference"})
# Who approves campaign content when no fix.approval.matrix rule names a
# group. A business ruling; Tier 2 (managers) is the default.
CREATIVE_APPROVER_PARAM = "cd_campaign.creative_approver_group"
CREATIVE_APPROVER_DEFAULT = "cd_entity_config.group_dofa_tier_2"


class FixCampaignCreative(models.Model):
    """Campaign content, approved through the M63 engine before launch.

    A03 audit G-M35-10: `state` had no methods and launch never read it, so
    "approved" was a value anyone could type. It now changes only through
    the transitions below, the approval is routed (`_approval_routed`), and
    an approved creative is frozen until it is withdrawn.
    """

    _name = "fix.campaign.creative"
    _description = "Marketing Creative Asset"
    _inherit = ["mail.thread", "fix.approvable.mixin"]
    _order = "name"

    _approval_domain = "creative"
    _approval_apply_method = "action_approve"
    _approval_routed = True

    name = fields.Char(required=True, tracking=True)
    campaign_id = fields.Many2one("fix.campaign", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="campaign_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(related="campaign_id.operating_unit_id", store=True)
    asset_type = fields.Selection(
        [("image", "Image"), ("video", "Video"), ("copy", "Copy"), ("landing", "Landing page")],
        required=True,
        default="image",
        tracking=True,
    )
    channel = fields.Char(tracking=True)
    reference = fields.Char(
        tracking=True,
        help="Exact asset reference (S3 key / URL) — never a fabricated path.",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("retired", "Retired")],
        required=True,
        default="draft",
        tracking=True,
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True, copy=False)
    approved_at = fields.Datetime(string="Approved At", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "approved_by_id", "approved_at"}

    def _content_frozen(self) -> bool:
        self.ensure_one()
        return self.state == "approved" or self.approval_state == "pending"

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self._content_frozen():
            locked |= CREATIVE_CONTENT_FIELDS
        return locked

    def write(self, vals):
        if not self.env.su and CREATIVE_CONTENT_FIELDS & set(vals):
            frozen = self.filtered(lambda r: r._content_frozen())
            if frozen:
                raise UserError(
                    "Creative '%s' is %s. Withdraw it (or recall the request) before "
                    "editing it; the edited content then needs a fresh approval."
                    % (
                        frozen[0].name,
                        "approved" if frozen[0].state == "approved" else "awaiting approval",
                    )
                )
        return super().write(vals)

    # --- the M63 engine ---------------------------------------------------
    def _approval_needed(self) -> bool:
        return self.state == "draft"

    def _approval_group_xmlid(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(CREATIVE_APPROVER_PARAM, CREATIVE_APPROVER_DEFAULT)
        )

    def action_request_approval(self, justification=None):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft creative can be sent for approval.")
            if not (rec.reference or "").strip():
                raise UserError(
                    "Creative '%s' has no asset reference. The approver must be able "
                    "to see exactly what is being approved." % rec.name
                )
        return super().action_request_approval(justification=justification)

    def action_approve(self):
        """Approve the content. Runs only from the approver's M63 task."""
        self._approval_assert_routed()
        group = self._approval_group_xmlid()
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft creative can be approved.")
            authority = rec._approval_authority_user()
            if group and not self.env.su and not authority.has_group(group):
                raise UserError(
                    "%s does not hold the authority to approve campaign content." % authority.name
                )
            makers = rec.create_uid | rec.approval_request_id.sudo().requested_by_id
            if not self.env.su and rec._approval_acting_users() & makers:
                raise UserError(
                    "Segregation of duties: the person who created or submitted a "
                    "creative cannot approve it."
                )
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": authority.id,
                    "approved_at": fields.Datetime.now(),
                }
            )
        return True

    def _approval_on_rejected(self, comment):
        self.message_post(body="Creative rejected: %s" % (comment or ""))

    def action_withdraw(self):
        """Back to draft so the content can be edited; the approval is void."""
        for rec in self:
            if rec.state != "approved":
                raise UserError("Only an approved creative can be withdrawn.")
            rec._guarded().write({"state": "draft", "approved_by_id": False, "approved_at": False})
            rec._approval_void("creative withdrawn for editing")
            rec.message_post(body="Creative withdrawn for editing; it needs a fresh approval.")
            # A03 audit W7: a running campaign kept sending the withdrawn
            # content. It pauses until the creative is approved again, and
            # Resume re-checks that.
            if rec.campaign_id.state == "running":
                rec.campaign_id.action_pause()
                rec.campaign_id.message_post(
                    body="Paused: creative %s was withdrawn for editing." % rec.display_name
                )
        return True

    def action_retire(self):
        for rec in self:
            if rec.state == "retired":
                raise UserError("This creative is already retired.")
            if rec.approval_state == "pending":
                rec._approval_void("creative retired while awaiting approval")
            elif rec.state == "approved":
                rec._approval_void("creative retired")
            rec._guarded().write({"state": "retired"})
        return True

    def action_reset_to_draft(self):
        for rec in self:
            if rec.state != "retired":
                raise UserError("Only a retired creative returns to draft.")
            rec._guarded().write({"state": "draft", "approved_by_id": False, "approved_at": False})
        return True


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
