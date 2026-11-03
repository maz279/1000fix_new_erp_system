# fix_campaign — M35: campaigns, attribution, bilingual content (P08-M04-T08, R06-M01-T05).
import logging
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

from libs.py import fix_btrc
from libs.py.fix_events import publish

_logger = logging.getLogger(__name__)

# Addressed channels message individual people: each needs a GRANTED
# fix.consent (cd_party_master) on that channel or the all-channel
# "marketing" consent. Social/search/billboard reach no individual recipient.
CHANNEL_CONSENTS = {
    "sms": ("sms", "marketing"),
    "email": ("email", "marketing"),
    "portal": ("push", "marketing"),
}
# Which fix.consent CHANNEL a campaign channel asks the S2 service about.
# The umbrella 'marketing' value is handled inside the service, so it is not
# repeated here — that expansion is exactly what the service owns.
CONSENT_CHANNEL_FOR = {"sms": "sms", "email": "email", "portal": "push"}
# Segments whose membership this module can resolve without another module's
# data; any other segment must state its audience_domain explicitly.
SELF_RESOLVED_SEGMENTS = {"all_customers": []}

# BTRC A2P directives bind channels that address an individual subscriber.
# Social, search and billboard reach no one in particular.
BTRC_REGULATED_CHANNELS = {"sms", "email", "portal"}
# Promotional traffic is permitted 08:00–22:00 Bangladesh Standard Time only.
#
# The CLOCK itself now lives in libs/py/fix_btrc, because the S1 notification
# delivery service (M27, cd_contact_centre) must enforce the same window on
# every outbound promotional message and cannot import this sibling module.
# These names are re-exported so nothing that already imports them breaks.
BTRC_CURFEW_OPEN_HOUR = fix_btrc.CURFEW_OPEN_HOUR
BTRC_CURFEW_CLOSE_HOUR = fix_btrc.CURFEW_CLOSE_HOUR
BST = fix_btrc.BST
# A DND scrub older than this no longer counts as evidence at launch.
BTRC_DND_SCRUB_MAX_AGE_HOURS = 24

# A03 audit G-M35-4: which campaign channels the DND registry EXCLUDES
# recipients from. The registry lists subscriber numbers, so SMS is bound by
# BTRC in any reading. Applying it to e-mail and portal too is the fail-closed
# default (a person who asked not to be disturbed is not messaged on another
# channel either); a business ruling can narrow it to "sms" with this
# ir.config_parameter. Comma-separated campaign channel codes.
DND_CHANNELS_PARAM = "cd_campaign.dnd_channels"
DND_CHANNELS_DEFAULT = "sms,email,portal"
# A03 audit G-M35-10: launch always refuses a campaign whose creatives are not
# all approved (or retired). Whether a campaign with NO creative at all may
# launch is a business ruling; "1" makes at least one approved creative
# mandatory. Default off keeps today's behaviour for creative-less campaigns.
CREATIVE_REQUIRED_PARAM = "cd_campaign.launch_requires_approved_creative"


def normalise_msisdn(number: str) -> str:
    """A Bangladeshi mobile number in the registry's 01XXXXXXXXX form.

    Party phones are stored as typed ("+880 1711-123456", "8801711123456",
    "01711123456"). The registry match has to see through that, or a listed
    subscriber is missed because of a space or a country code (G-M35-4).
    """
    digits = "".join(ch for ch in (number or "") if ch.isdigit())
    if digits.startswith("880"):
        digits = digits[2:]
    elif digits.startswith("1") and len(digits) == 10:
        digits = "0" + digits
    return digits


class FixCampaign(models.Model):
    """Marketing campaigns with audience segmentation, PDPA consent filtering,
    response attribution ledger, and M10 loyalty integration hooks."""

    _name = "fix.campaign"
    _description = "Marketing Campaign"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.dofa.mixin"]

    # A03 audit R7: a budget above Tier 0 is approved from the approver's
    # M63 inbox (Request Approval), never by pressing Approve Budget directly.
    _approval_domain = "campaign_budget"
    _approval_apply_method = "action_approve_budget"
    _approval_routed = True
    _order = "start_date desc"

    # REQ-35.3 promotional budget thresholds in BDT. REQ text and DOFA matrix
    # disagree (REQ: >50,000 Tier 3, >200,000 Tier 4; matrix: <=25,000 Tier 2,
    # <=100,000 Tier 3, >100,000 Tier 4). REQ text is implemented.
    _DOFA_BUDGET_THRESHOLDS = [
        (50000.0, "tier_0"),
        (200000.0, "tier_3"),
        (float("inf"), "tier_4"),
    ]

    def _dofa_amount(self) -> float:
        self.ensure_one()
        return self.budget or 0.0

    def _dofa_thresholds(self):
        return self._DOFA_BUDGET_THRESHOLDS

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "a promotional budget of BDT %.2f" % (self.budget or 0.0)

    @api.depends("budget")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def _fix_guarded_fields(self) -> set:
        # Launch state, the budget sign-off, the consented audience and the
        # BTRC evidence are set by the actions below. A direct write put two
        # SMS campaigns into 'running' with no consent filter, DND scrub or
        # budget approval (A03 audit).
        return super()._fix_guarded_fields() | {
            "state",
            "budget_approved",
            "budget_approver_id",
            "budget_approval_date",
            "recipient_ids",
            "pdpa_consent_verified",
            "excluded_no_consent_count",
            "dnd_scrubbed_at",
            "dnd_excluded_count",
            "dnd_excluded_partner_ids",
            "dispatch_hold_until",
        }

    def _dofa_tier_label(self, tier: str) -> str:
        return dict(self._fields["dofa_tier_required"].selection).get(tier, tier)

    def _dofa_void_approval(self, reason: str):
        # The campaign's own budget flag says the same thing as the DOFA stamp
        # and must fall with it, or the constraint below refuses the void.
        self._withdraw_budget_flag()
        return super()._dofa_void_approval(reason)

    def _withdraw_budget_flag(self):
        self.filtered("budget_approved")._guarded().write(
            {"budget_approved": False, "budget_approver_id": False, "budget_approval_date": False}
        )

    def write(self, vals):
        """A budget raised after sign-off is not the budget that was signed off.

        The approval is withdrawn BEFORE the new budget is written, so the
        authorisation constraint sees an unapproved campaign rather than an
        approved one that is suddenly over its authority (A03 audit, R4).
        """
        if "budget" in vals:
            new_budget = vals.get("budget") or 0.0
            for rec in self.filtered("budget_approved"):
                if new_budget > (rec.budget or 0.0) + 0.005:
                    reason = (
                        "the budget rose from BDT %.2f to BDT %.2f after approval; "
                        "re-approval is required." % (rec.budget or 0.0, new_budget)
                    )
                    if rec.dofa_approved:
                        rec._dofa_void_approval(reason)
                    else:
                        rec._withdraw_budget_flag()
                        rec.message_post(body="Budget approval withdrawn: %s" % reason)
        return super().write(vals)

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, tracking=True)
    name_bn = fields.Char(string="Campaign (Bengali)", help="DE-17 bilingual branding")
    channel = fields.Selection(
        [
            ("social", "Social Media"),
            ("search", "Search Engines"),
            ("sms", "Direct SMS"),
            ("email", "Email Newsletter"),
            ("billboard", "Billboard / Outdoor"),
            ("portal", "Customer Portal Banner"),
        ],
        required=True,
        default="social",
        tracking=True,
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    budget = fields.Monetary(string="Budget", currency_field="currency_id", tracking=True)
    budget_approved = fields.Boolean(
        string="Budget Approved",
        default=False,
        tracking=True,
        help="Finance DOFA sign-off required for campaign budget release (FLAW-35.1)",
    )
    budget_approver_id = fields.Many2one(
        "res.users",
        string="Budget Approver",
        tracking=True,
        help="Finance or marketing executive approving the campaign budget",
    )
    budget_memo_ref = fields.Char(
        string="Budget Memo Reference",
        tracking=True,
        help="Internal finance memo / requisition reference for budget allocation",
    )
    budget_approval_date = fields.Datetime(
        string="Budget Approval Date",
        readonly=True,
        copy=False,
    )

    # --- BTRC A2P SMS compliance (REQ-35.1, REQ-35.2, REQ-35.4) ------------
    # The audit of 2026-10-31 found all three of these described in UI label
    # text and enforced nowhere: a campaign launched at 03:00 BST succeeded,
    # "DND" in the workspace was PDPA consent relabelled, and there was no
    # sender mask or opt-out anywhere in the module.
    dnd_scrubbed_at = fields.Datetime(
        string="DND Registry Scrubbed At",
        readonly=True,
        copy=False,
        tracking=True,
        help="When this audience was last checked against the BTRC national "
        "Do-Not-Disturb registry. REQ-35.1 requires a scrub within 24 hours "
        "of launch.",
    )
    dnd_excluded_count = fields.Integer(
        string="Excluded by DND Registry",
        readonly=True,
        copy=False,
        help="Recipients removed because they are on the BTRC DND registry. "
        "Distinct from excluded_no_consent_count, which is PDPA consent.",
    )
    dnd_excluded_partner_ids = fields.Many2many(
        "res.partner",
        "fix_campaign_dnd_excluded_rel",
        "campaign_id",
        "partner_id",
        string="Excluded by DND (Parties)",
        readonly=True,
        copy=False,
        help="Who the last scrub or launch removed for being on the DND "
        "registry. The scrub is evidence only if it says whom it excluded "
        "(A03 audit G-M35-4).",
    )
    btrc_sender_mask = fields.Char(
        string="BTRC Approved Sender ID",
        default="1000FiX",
        tracking=True,
        help="Registered A2P sender mask. BTRC rejects unmasked promotional traffic.",
    )
    dispatch_hold_until = fields.Datetime(
        string="Held Until (BTRC Curfew)",
        readonly=True,
        copy=False,
        tracking=True,
        help="REQ-35.2: set when a launch lands outside 08:00-22:00 BST. The "
        "campaign is queued and released by cron when the window opens.",
    )
    sms_opt_out_text = fields.Char(
        string="Opt-Out Instruction",
        default="Stop SMS: Send STOP to 16743",
        help="REQ-35.4 requires every promotional SMS to carry an opt-out instruction.",
    )
    start_date = fields.Date(tracking=True)
    end_date = fields.Date(tracking=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("running", "Running"),
            ("paused", "Paused"),
            ("completed", "Completed"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )

    # Audience segmentation & PDPA Consent (M35 + R03 compliance)
    target_audience_type = fields.Selection(
        [
            ("all_customers", "All Registered Customers"),
            ("active_warranty", "Active Warranty Holders"),
            ("corporate_amc", "Corporate AMC Clients"),
            ("dormant_90d", "Dormant (90+ Days)"),
            ("custom_domain", "Custom Demographic Segment"),
        ],
        default="all_customers",
        required=True,
        tracking=True,
        string="Target Segment",
    )
    audience_domain = fields.Char(
        string="Audience Segment Domain",
        help="res.partner domain filter, e.g. [('city','=','Dhaka')]",
    )
    pdpa_consent_verified = fields.Boolean(
        string="PDPA Consent Filter Verified",
        default=False,
        readonly=True,
        copy=False,
        help="Set at launch ONLY after the audience was filtered against granted "
        "fix.consent records for the campaign channel",
    )
    recipient_ids = fields.Many2many(
        "res.partner",
        "fix_campaign_recipient_rel",
        "campaign_id",
        "partner_id",
        string="Consented Recipients",
        readonly=True,
        copy=False,
        help="The audience members with a granted consent at launch",
    )
    recipient_count = fields.Integer(compute="_compute_recipient_count")
    excluded_no_consent_count = fields.Integer(
        string="Excluded (No Consent)", readonly=True, copy=False
    )

    # Tracking & Attribution
    utm_source = fields.Char(string="UTM Source", default="1000fix")
    utm_medium = fields.Char(string="UTM Medium", default="cpc")
    utm_campaign = fields.Char(
        string="UTM Campaign Code", compute="_compute_utm_campaign", store=True
    )

    response_ids = fields.One2many("fix.campaign.response", "campaign_id", string="Responses")
    response_count = fields.Integer(compute="_compute_response_count", string="Response Count")
    cost_per_response = fields.Monetary(
        string="Cost per Response", currency_field="currency_id", compute="_compute_response_count"
    )
    journey_ids = fields.One2many("fix.campaign.journey", "campaign_id", string="Journeys")
    creative_ids = fields.One2many("fix.campaign.creative", "campaign_id", string="Creatives")
    creative_unapproved_count = fields.Integer(
        string="Creatives Not Approved",
        compute="_compute_creative_unapproved_count",
        help="Live (not retired) creatives still awaiting approval. Launch "
        "refuses while this is above zero (A03 audit G-M35-10).",
    )

    # Budget versus actual (A03 audit §4.7 step 8). Actual spend is what the
    # estate RECORDED: the S1 per-message cost of this campaign's sends and
    # the discount its offers have given away. Media buys outside the estate
    # are not on file and are not estimated.
    actual_spend = fields.Monetary(
        string="Actual Spend (Recorded)",
        currency_field="currency_id",
        compute="_compute_budget_actual",
        help="Message cost charged by S1 for this campaign's sends plus offer "
        "discounts redeemed. Spend booked outside the estate is not included.",
    )
    budget_variance = fields.Monetary(
        string="Budget Remaining",
        currency_field="currency_id",
        compute="_compute_budget_actual",
        help="Budget minus recorded actual spend. Negative means overspent.",
    )
    budget_utilisation_pct = fields.Float(
        string="Budget Used (%)", compute="_compute_budget_actual", digits=(16, 1)
    )

    @api.depends("name", "channel")
    def _compute_utm_campaign(self):
        for rec in self:
            safe_name = (rec.name or "campaign").lower().replace(" ", "_").replace("/", "_")
            rec.utm_campaign = f"{safe_name}_{rec.channel}"

    @api.depends("recipient_ids")
    def _compute_recipient_count(self):
        for rec in self:
            rec.recipient_count = len(rec.recipient_ids)

    def _audience_domain(self):
        """The segment's res.partner domain (before consent filtering)."""
        self.ensure_one()
        if self.audience_domain:
            try:
                domain = safe_eval(self.audience_domain)
            except Exception as exc:
                raise UserError("Audience segment domain is not valid: %s" % exc) from exc
            if not isinstance(domain, list | tuple):
                raise UserError("Audience segment domain must be a list")
            domain = list(domain)
        elif self.target_audience_type in SELF_RESOLVED_SEGMENTS:
            domain = list(SELF_RESOLVED_SEGMENTS[self.target_audience_type])
        else:
            raise UserError(
                "Segment '%s' needs an explicit audience segment domain"
                % dict(self._fields["target_audience_type"].selection)[self.target_audience_type]
            )
        return domain

    def _consented(self, domain):
        """The segment partners the M33 consent service clears for this send.

        This used to be a local implementation that filtered by CHANNEL ONLY
        and never looked at the processing purpose, so a party who had opted
        in to service_updates on SMS was counted as consenting to marketing
        SMS. It now delegates to the single S2 decision procedure
        (fix.consent.consent_check_bulk), which filters on purpose AND
        channel and applies the same latest-decision-wins rule everywhere.

        Marketing campaigns always process for the 'marketing' purpose; the
        'marketing' all-channel umbrella consent still satisfies it, so an
        existing all-channel opt-in keeps working exactly as before.
        """
        self.ensure_one()
        partners = self.env["res.partner"].search(domain)
        allowed, _excluded = self.env["fix.consent"].consent_check_bulk(
            partners, "marketing", CONSENT_CHANNEL_FOR[self.channel], company=self.company_id
        )
        return allowed

    @api.depends("response_ids", "budget")
    def _compute_response_count(self):
        for rec in self:
            rec.response_count = len(rec.response_ids)
            rec.cost_per_response = (
                round(rec.budget / len(rec.response_ids), 2) if rec.response_ids else 0.0
            )

    @api.depends("creative_ids.state")
    def _compute_creative_unapproved_count(self):
        for rec in self:
            rec.creative_unapproved_count = len(
                rec.creative_ids.filtered(lambda c: c.state not in ("approved", "retired"))
            )

    def _recorded_spend(self) -> float:
        """S1 message cost of this campaign's sends plus offer discounts given."""
        self.ensure_one()
        if not self.id:
            return 0.0
        members = (
            self.env["fix.campaign.journey.member"]
            .sudo()
            .search([("journey_id.campaign_id", "=", self.id)])
        )
        Delivery = self.env["fix.notif.delivery"].sudo()
        rows = Delivery.search(
            [
                "|",
                "&",
                ("source_model", "=", "fix.campaign"),
                ("source_id", "=", self.id),
                "&",
                ("source_model", "=", "fix.campaign.journey.member"),
                ("source_id", "in", members.ids or [0]),
            ]
        )
        offers = self.env["fix.campaign.offer"].sudo().search([("campaign_id", "=", self.id)])
        return sum(rows.mapped("cost")) + sum(offers.mapped("total_redeemed_bdt"))

    @api.depends("budget")
    def _compute_budget_actual(self):
        for rec in self:
            spend = rec._recorded_spend()
            rec.actual_spend = spend
            rec.budget_variance = (rec.budget or 0.0) - spend
            rec.budget_utilisation_pct = round(spend / rec.budget * 100.0, 1) if rec.budget else 0.0

    # --- BTRC DND registry (A03 audit G-M35-4) ------------------------------
    def _dnd_applies(self) -> bool:
        """Whether this campaign's channel is bound by the DND registry."""
        self.ensure_one()
        raw = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(DND_CHANNELS_PARAM, DND_CHANNELS_DEFAULT)
        )
        channels = {c.strip() for c in (raw or "").split(",") if c.strip()}
        return self.channel in channels

    @api.model
    def _dnd_listed(self, partners):
        """The parties among `partners` whose phone is on the active registry."""
        by_number = {}
        for partner in partners:
            for number in (partner.phone, getattr(partner, "mobile", False)):
                key = normalise_msisdn(number)
                if key:
                    by_number.setdefault(key, self.env["res.partner"])
                    by_number[key] |= partner
        if not by_number:
            return self.env["res.partner"]
        # The registry may hold numbers as typed too, so both the raw and the
        # normalised forms are matched, and then normalised again here.
        candidates = set(by_number)
        for key in list(by_number):
            candidates |= {"+880" + key[1:], "880" + key[1:]}
        rows = (
            self.env["fix.dnd.registry"]
            .sudo()
            .search([("msisdn", "in", list(candidates)), ("active", "=", True)])
        )
        listed = self.env["res.partner"]
        for row in rows:
            listed |= by_number.get(normalise_msisdn(row.msisdn), self.env["res.partner"])
        return listed

    def _dnd_reachable(self, partners):
        """`partners` minus the DND-listed ones, when this channel is bound."""
        self.ensure_one()
        if not partners or not self._dnd_applies():
            return partners
        return partners - self._dnd_listed(partners)

    def _audience_after_scrub(self):
        """(consented and reachable, excluded by DND) for an addressed channel."""
        self.ensure_one()
        consented = self._consented(self._audience_domain())
        reachable = self._dnd_reachable(consented)
        return reachable, consented - reachable

    # --- BTRC enforcement -------------------------------------------------
    # The three methods below DELEGATE to libs/py/fix_btrc. They keep their
    # names because the zero-trust certification suite drives them directly;
    # the arithmetic lives in the library so M27's delivery service applies
    # exactly the same window (gap-plan: "call it, don't copy it").
    @api.model
    def _btrc_now_bst(self):
        """Current wall-clock time in Bangladesh Standard Time."""
        return fix_btrc.now_bst(fields.Datetime.now())

    def _btrc_within_curfew(self) -> bool:
        """True when the clock is inside the permitted 08:00–22:00 BST window."""
        return fix_btrc.within_curfew(fields.Datetime.now())

    @api.model
    def _btrc_next_window_open(self):
        """The next 08:00 BST, as a naive UTC datetime for storage."""
        return fix_btrc.next_window_open(fields.Datetime.now())

    def _hold_for_curfew(self):
        """REQ-35.2: park the campaign until the window opens, rather than
        dispatching into the prohibited 22:00-08:00 period."""
        for rec in self:
            opens = rec._btrc_next_window_open()
            rec._guarded().write({"dispatch_hold_until": opens, "state": "draft"})
            rec.message_post(
                body="Held by the BTRC promotional curfew: dispatch is permitted "
                "from %s BST (08:00-22:00 window, REQ-35.2)." % opens
            )
            publish(
                self.env,
                "campaign.curfew_held",
                "fix.campaign",
                rec.id,
                {"campaign": rec.name, "channel": rec.channel, "release_at": str(opens)},
            )

    def _dnd_scrub_is_stale(self) -> bool:
        self.ensure_one()
        if not self.dnd_scrubbed_at:
            return True
        age = fields.Datetime.now() - self.dnd_scrubbed_at
        return age > timedelta(hours=BTRC_DND_SCRUB_MAX_AGE_HOURS)

    @api.model
    def cron_release_curfew_holds(self):
        """Launch campaigns whose curfew hold has expired.

        Each campaign is released inside its own savepoint. One held campaign
        that could no longer launch used to raise inside the loop and abort
        the whole run, so every other due campaign stayed held (A03 audit
        G-M35-7). A failure now rolls back that campaign only, clears its hold
        so the cron stops retrying it every 15 minutes, and says why on the
        campaign.

        The release IS the launch moment, so a DND scrub that went stale
        while the campaign waited for 08:00 is re-run here: the registry
        lookup is mechanical, and REQ-35.1 asks for a scrub within 24 hours
        of launch, which a fresh one is.
        """
        due = self.search(
            [
                ("state", "=", "draft"),
                ("dispatch_hold_until", "!=", False),
                ("dispatch_hold_until", "<=", fields.Datetime.now()),
            ]
        )
        released, failed = 0, 0
        for rec in due:
            if not rec._btrc_within_curfew():
                continue
            try:
                with self.env.cr.savepoint():
                    rec._guarded().write({"dispatch_hold_until": False})
                    if rec.channel in BTRC_REGULATED_CHANNELS and rec._dnd_scrub_is_stale():
                        rec.action_scrub_dnd()
                    rec.action_launch()
                released += 1
            except Exception as exc:  # one campaign must not hold back the rest
                failed += 1
                _logger.warning("curfew release of campaign %s failed: %s", rec.id, exc)
                reason = (
                    exc.args[0]
                    if isinstance(exc, UserError | ValidationError)
                    else ("an unexpected error occurred (see the server log)")
                )
                rec._guarded().write({"dispatch_hold_until": False})
                rec.message_post(
                    body="The BTRC curfew hold expired but the campaign could not be "
                    "launched, so it stays in draft: %s Fix this and launch it again." % reason
                )
        return {"released": released, "failed": failed}

    def action_scrub_dnd(self):
        """REQ-35.1: scrub the audience against the BTRC Do-Not-Disturb registry.

        The scrub used to COUNT the listed numbers and leave those parties in
        the audience, so a DND subscriber still received the marketing SMS
        (A03 audit G-M35-4). It now records who is excluded, and launch
        removes exactly those parties (re-checked live, because the registry
        may change between scrub and launch).
        """
        for rec in self:
            if rec.state != "draft":
                raise UserError(
                    "Scrub the audience before launch. A running campaign's "
                    "recipients were fixed, and scrubbed, when it launched."
                )
            if rec.channel in CHANNEL_CONSENTS:
                reachable, blocked = rec._audience_after_scrub()
            else:
                reachable = blocked = self.env["res.partner"]
            rec._guarded().write(
                {
                    "dnd_scrubbed_at": fields.Datetime.now(),
                    "dnd_excluded_count": len(blocked),
                    "dnd_excluded_partner_ids": [(6, 0, blocked.ids)],
                }
            )
            rec.message_post(
                body="BTRC DND scrub completed: %d of %d consented recipients are on "
                "the national Do-Not-Disturb registry and are excluded from this "
                "campaign." % (len(blocked), len(reachable) + len(blocked))
            )
        return True

    def _assert_btrc_launch_allowed(self):
        """REQ-35.1/35.2/35.4 gate, applied to addressed promotional channels."""
        self.ensure_one()
        if not self.dnd_scrubbed_at:
            raise UserError(
                "BTRC Do-Not-Disturb: this audience has never been scrubbed "
                "against the national DND registry. Run the DND scrub before "
                "launching (REQ-35.1)."
            )
        age = fields.Datetime.now() - self.dnd_scrubbed_at
        if self._dnd_scrub_is_stale():
            raise UserError(
                "BTRC Do-Not-Disturb: the last DND scrub was %d hours ago and is "
                "no longer valid. Re-scrub within %d hours of launch (REQ-35.1)."
                % (age.total_seconds() // 3600, BTRC_DND_SCRUB_MAX_AGE_HOURS)
            )
        if self.channel == "sms":
            if not (self.btrc_sender_mask or "").strip():
                raise UserError(
                    "BTRC sender ID: a registered sender mask is required on "
                    "promotional SMS (REQ-35.4)."
                )
            if not (self.sms_opt_out_text or "").strip():
                raise UserError(
                    "BTRC opt-out: promotional SMS must carry an opt-out "
                    "instruction such as 'Stop SMS: Send STOP to 16743' (REQ-35.4)."
                )

    @api.constrains("budget_approved", "budget", "dofa_approved")
    def _check_budget_approval_is_authorised(self):
        """REQ-35.3: above the threshold, budget_approved is only legitimate
        when DOFA granted it. Without this a direct write set the flag and the
        launch gate waved the campaign through — the action-only weakness the
        A03 audit found across this area."""
        for rec in self:
            if not rec.budget_approved:
                continue
            tier = rec._dofa_current_tier()
            if tier == "tier_0":
                continue
            if not rec.dofa_approved:
                raise ValidationError(
                    "Budget approval of %s requires a recorded DOFA sign-off (%s). "
                    "Use Approve Budget rather than setting the flag directly "
                    "(REQ-35.3)." % (rec._dofa_amount_label(), rec._dofa_tier_label(tier))
                )

    def action_approve_budget(self):
        """Formal finance DOFA sign-off on campaign budget (REQ-35.3)."""
        for rec in self:
            if rec.budget <= 0:
                raise UserError("A campaign budget must be greater than zero to require approval.")
            if not rec.budget_memo_ref:
                raise UserError(
                    "A valid budget memo reference is required to approve campaign expenditure."
                )
            if rec._dofa_current_tier() != "tier_0":
                # Derives the tier, checks the approver holds it, and refuses
                # self-approval.
                rec.action_dofa_approve()
            rec._guarded().write(
                {
                    "budget_approved": True,
                    "budget_approver_id": self.env.user.id,
                    "budget_approval_date": fields.Datetime.now(),
                }
            )

    def action_launch(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Launch from draft only")
            if not rec.start_date or not rec.end_date:
                raise UserError("A campaign runs between dates")
            if rec.end_date < rec.start_date:
                raise UserError("Campaign window is inverted")
            # REQ-35.3: the tier comes from the DOFA ladder (the coded REQ
            # bands, or whichever ladder M30 has put in force), not from
            # literals here that a ruling could never move. The message names
            # the tier because that is what the operator has to go and obtain.
            tier = rec._dofa_current_tier()
            if tier != "tier_0":
                if not rec.budget_approved:
                    raise UserError(
                        "Launch blocked: %s requires %s sign-off (approve the budget "
                        "first) (REQ-35.3)."
                        % (rec._dofa_amount_label(), rec._dofa_tier_label(tier))
                    )
                # The flag says somebody approved A budget; this says the
                # approval still covers THIS budget. Without it a budget
                # approved at 150,000 launched after being raised to
                # 5,000,000 (A03 audit).
                rec._dofa_assert_approved("Campaign launch")
            rec._assert_creatives_approved()
            vals = {"state": "running"}
            if rec.channel in CHANNEL_CONSENTS:
                # PDPA: only partners with a granted consent are messaged, and
                # BTRC: nobody on the DND registry is. The registry is
                # re-checked here rather than trusted from the scrub, because
                # it can change between the two (A03 audit G-M35-4).
                domain = rec._audience_domain()
                audience_size = self.env["res.partner"].search_count(domain)
                consented = rec._consented(domain)
                if not consented:
                    raise UserError(
                        "No audience member has a granted %s consent - nothing to send"
                        % rec.channel
                    )
                recipients = rec._dnd_reachable(consented)
                blocked = consented - recipients
                if not recipients:
                    raise UserError(
                        "Every consented audience member is on the BTRC Do-Not-Disturb "
                        "registry - nothing to send (REQ-35.1)."
                    )
                vals.update(
                    {
                        "recipient_ids": [(6, 0, recipients.ids)],
                        "excluded_no_consent_count": audience_size - len(consented),
                        "pdpa_consent_verified": True,
                        "dnd_excluded_count": len(blocked),
                        "dnd_excluded_partner_ids": [(6, 0, blocked.ids)],
                    }
                )
            # REQ-35.1 / 35.2 / 35.4: BTRC binds addressed promotional
            # channels only — social, search and billboard reach no individual
            # subscriber. Checked after the audience resolves, so a campaign
            # with nobody to send to reports that, not a curfew.
            if rec.channel in BTRC_REGULATED_CHANNELS:
                rec._assert_btrc_launch_allowed()
                if not rec._btrc_within_curfew():
                    rec._hold_for_curfew()
                    continue

            rec._guarded().write(vals)
            publish(
                self.env,
                "campaign.launched",
                "fix.campaign",
                rec.id,
                {
                    "campaign": rec.name,
                    "channel": rec.channel,
                    "target_segment": rec.target_audience_type,
                    "pdpa_consent_verified": rec.pdpa_consent_verified,
                    "recipients": len(rec.recipient_ids),
                    "excluded_no_consent": rec.excluded_no_consent_count,
                },
            )
            rec._start_journeys()
        return True

    def _assert_creatives_approved(self):
        """A03 audit G-M35-10: content goes out only once it is approved.

        Every live creative must be approved; a retired one no longer counts.
        Whether a campaign with no creative at all may launch is a business
        ruling (CREATIVE_REQUIRED_PARAM, default: it may).
        """
        self.ensure_one()
        live = self.creative_ids.filtered(lambda c: c.state != "retired")
        waiting = live.filtered(lambda c: c.state != "approved")
        if waiting:
            raise UserError(
                "Launch blocked: %d creative(s) are not approved yet (%s). Request "
                "approval for each, or retire the ones this campaign will not use."
                % (len(waiting), ", ".join(waiting.mapped("name")))
            )
        required = self.env["ir.config_parameter"].sudo().get_param(CREATIVE_REQUIRED_PARAM, "0")
        if required in ("1", "True", "true") and not live:
            raise UserError(
                "Launch blocked: this campaign has no approved creative. Add its "
                "content as a creative and have it approved first."
            )

    def _start_journeys(self) -> int:
        """Start sending: activate the campaign's journeys that have steps.

        A03 audit G-M35-9: launch used to set 'running' and stop, so an SMS
        campaign reported recipients and delivered nothing. Sending stays
        journey-only, because a journey step is the one path that queues
        through S1 with the consent, curfew and DND checks re-run before each
        message. A 'campaign audience' journey enrols exactly the recipients
        launch just filtered; a segment journey enrols its segment; a trigger
        journey starts listening for its event.
        """
        self.ensure_one()
        startable = self.journey_ids.filtered(
            lambda j: j.state == "draft" and j.active and j.step_ids
        )
        for journey in startable:
            journey.action_activate()
        if not startable and not self.journey_ids.filtered(lambda j: j.state == "active"):
            self.message_post(
                body="Launched with no journey to send through: nothing is sent until a "
                "journey with steps is added and activated."
            )
        return len(startable)

    def action_pause(self):
        """Pausing a campaign pauses its journeys (A03 audit G-M35-5).

        Journey eligibility looks at the journey's own state, so a paused
        campaign used to keep sending through its active journeys. Only the
        journeys this pause stops are resumed by Resume.
        """
        for rec in self:
            if rec.state != "running":
                raise UserError("Only a RUNNING campaign pauses")
            rec._guarded().write({"state": "paused"})
            rec.journey_ids.filtered(lambda j: j.state == "active")._pause_for_campaign()
        return True

    def action_resume(self):
        for rec in self:
            if rec.state != "paused":
                raise UserError("Only a PAUSED campaign resumes")
            rec._guarded().write({"state": "running"})
            rec.journey_ids.filtered("paused_by_campaign")._resume_for_campaign()
        return True

    def action_complete(self):
        for rec in self:
            if rec.state not in ("running", "paused"):
                raise UserError("Complete an active campaign")
            rec._guarded().write({"state": "completed"})
            # A completed campaign sends nothing more; its journeys stop and
            # are not resumable through the campaign.
            rec.journey_ids.filtered(lambda j: j.state == "active")._pause_for_campaign()
            rec.journey_ids._guarded().write({"paused_by_campaign": False})
            publish(
                self.env,
                "campaign.completed",
                "fix.campaign",
                rec.id,
                {
                    "campaign": rec.name,
                    "responses": rec.response_count,
                    "cost_per_response": rec.cost_per_response,
                },
            )
            rec.message_post(
                body="Campaign completed. Budget BDT %.2f, recorded actual spend BDT %.2f "
                "(%.1f%% used)." % (rec.budget or 0.0, rec.actual_spend, rec.budget_utilisation_pct)
            )
        return True

    @api.model
    def cron_complete_ended_campaigns(self):
        """Complete running or paused campaigns whose end date has passed.

        A03 audit §4.7 step 8: nothing closed a campaign at its end date, so
        an Eid campaign kept its journeys sending into the following month.
        Each campaign completes in its own savepoint, so one that cannot does
        not hold back the rest.
        """
        today = fields.Date.context_today(self)
        due = self.search([("state", "in", ("running", "paused")), ("end_date", "<", today)])
        done = 0
        for rec in due:
            try:
                with self.env.cr.savepoint():
                    rec.action_complete()
                done += 1
            except Exception as exc:  # one campaign must not hold back the rest
                _logger.warning("auto-complete of campaign %s failed: %s", rec.id, exc)
        return {"due": len(due), "completed": done}

    def action_trigger_loyalty_hook(self):
        """Consume M10 campaign hooks (R03): each responder with a party that has
        not been rewarded yet receives the reward of the campaign's first ACTIVE
        loyalty hook, disbursed BY the hook (posted ledger line or voucher).
        Returns the number of responses rewarded.

        Fixed (R01 coverage pass): ``env.get()`` returns an EMPTY recordset, which
        is falsy, so the hook branch never ran; the hook was then called through a
        method name it does not have, so no point was ever posted while responses
        were still marked rewarded; and the ``return`` inside the loop silently
        skipped every campaign after the first."""
        self.ensure_one()
        hooks = self.env.get("fix.loyalty.campaign.hook")  # None when M10 is not installed
        awarded_count = 0
        if hooks is not None:
            for hook in hooks.search([("campaign_id", "=", self.id), ("state", "=", "active")]):
                for resp in self.response_ids.filtered(
                    lambda r: r.partner_id and r.conversion_status != "enrolled_loyalty"
                ):
                    hook.action_execute_campaign_rewards(resp.partner_id)
                    resp.write(
                        {
                            "loyalty_points_awarded": hook.bonus_points
                            if hook.reward_type == "bonus_points"
                            else 0,
                            "conversion_status": "enrolled_loyalty",
                        }
                    )
                    awarded_count += 1
        publish(
            self.env,
            "campaign.loyalty_rewards_disbursed",
            "fix.campaign",
            self.id,
            {
                "campaign": self.name,
                "rewards_awarded": awarded_count,
                "hook_type": "M10_R03_CampaignHook",
            },
        )
        return awarded_count


class FixCampaignResponse(models.Model):
    """The attribution ledger: demand generation is measurable per spend."""

    _name = "fix.campaign.response"
    _description = "Campaign Response"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "responded_at desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    campaign_id = fields.Many2one("fix.campaign", required=True, ondelete="cascade", index=True)
    partner_id = fields.Many2one("res.partner", string="Lead / Customer", ondelete="set null")
    response_type = fields.Selection(
        [
            ("click", "Click"),
            ("call", "Inbound Call"),
            ("form", "Form Submission"),
            ("visit", "Branch Visit"),
            ("service_booking", "Service Booking"),
        ],
        required=True,
        default="click",
    )
    conversion_status = fields.Selection(
        [
            ("engaged", "Engaged"),
            ("converted", "Converted to Order"),
            ("enrolled_loyalty", "Enrolled in Loyalty Program"),
        ],
        default="engaged",
        tracking=True,
    )
    loyalty_points_awarded = fields.Integer(string="Bonus Points Awarded", default=0)
    responded_at = fields.Datetime(default=fields.Datetime.now, required=True)

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        for rec in recs:
            publish(
                self.env,
                "campaign.response",
                "fix.campaign.response",
                rec.id,
                {
                    "campaign": rec.campaign_id.name,
                    "type": rec.response_type,
                    "conversion_status": rec.conversion_status,
                },
            )
        return recs
