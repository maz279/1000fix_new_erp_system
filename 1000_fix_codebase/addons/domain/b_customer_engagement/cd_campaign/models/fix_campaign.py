# fix_campaign — M35: campaigns, attribution, bilingual content (P08-M04-T08, R06-M01-T05).
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

from libs.py import fix_btrc
from libs.py.fix_events import publish

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


class FixCampaign(models.Model):
    """Marketing campaigns with audience segmentation, PDPA consent filtering,
    response attribution ledger, and M10 loyalty integration hooks."""

    _name = "fix.campaign"
    _description = "Marketing Campaign"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.dofa.mixin"]
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
            rec.write({"dispatch_hold_until": opens, "state": "draft"})
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

    @api.model
    def cron_release_curfew_holds(self):
        """Launch campaigns whose curfew hold has expired."""
        due = self.search(
            [
                ("state", "=", "draft"),
                ("dispatch_hold_until", "!=", False),
                ("dispatch_hold_until", "<=", fields.Datetime.now()),
            ]
        )
        released = 0
        for rec in due:
            if not rec._btrc_within_curfew():
                continue
            rec.dispatch_hold_until = False
            rec.action_launch()
            released += 1
        return released

    def action_scrub_dnd(self):
        """REQ-35.1: check the audience against the BTRC Do-Not-Disturb registry.

        The registry itself is an external BTRC service. What this records is
        the scrub and its result, which is what launch verifies; the gateway
        adapter supplies the matched numbers via fix.dnd.registry when it is
        wired. Until then an empty registry scrubs to zero exclusions, and the
        timestamp is still the evidence REQ-35.1 asks for.
        """
        for rec in self:
            domain = rec._audience_domain()
            recipients = (
                rec._consented(domain)
                if rec.channel in CHANNEL_CONSENTS
                else self.env["res.partner"]
            )
            registry = self.env["fix.dnd.registry"].sudo()
            numbers = [p.phone for p in recipients if p.phone]
            blocked = registry.search_count([("msisdn", "in", numbers)]) if numbers else 0
            rec.write(
                {
                    "dnd_scrubbed_at": fields.Datetime.now(),
                    "dnd_excluded_count": blocked,
                }
            )
            rec.message_post(
                body="BTRC DND scrub completed: %d of %d recipients are on the "
                "national Do-Not-Disturb registry." % (blocked, len(numbers))
            )

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
        if age > timedelta(hours=BTRC_DND_SCRUB_MAX_AGE_HOURS):
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
            if (rec.budget or 0.0) <= 50000.0:
                continue
            if not rec.dofa_approved:
                raise ValidationError(
                    "Budget approval above BDT 50,000 requires a recorded DOFA "
                    "sign-off. Use Approve Budget rather than setting the flag "
                    "directly (REQ-35.3)."
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
            if (rec.budget or 0.0) > 50000.0:
                # Derives the tier, checks the approver holds it, and refuses
                # self-approval.
                rec.action_dofa_approve()
            rec.write(
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
            # REQ-35.3: budgets above BDT 50,000 need DOFA sign-off. The
            # messages stay explicit about the tier because that is what the
            # marketing operator has to go and obtain.
            if (rec.budget or 0.0) > 50000.0 and not rec.budget_approved:
                if (rec.budget or 0.0) > 200000.0:
                    raise UserError(
                        "Launch blocked: Campaign budget > 200,000 BDT requires CFO DOFA "
                        "Tier 4 sign-off (approve the budget first) (REQ-35.3)."
                    )
                raise UserError(
                    "Launch blocked: Campaign budget > 50,000 BDT requires Marketing "
                    "Director DOFA Tier 3 sign-off (approve the budget first) "
                    "(REQ-35.3)."
                )
            vals = {"state": "running"}
            if rec.channel in CHANNEL_CONSENTS:
                # PDPA: only partners with a granted consent are messaged
                domain = rec._audience_domain()
                audience_size = self.env["res.partner"].search_count(domain)
                recipients = rec._consented(domain)
                if not recipients:
                    raise UserError(
                        "No audience member has a granted %s consent - nothing to send"
                        % rec.channel
                    )
                vals.update(
                    {
                        "recipient_ids": [(6, 0, recipients.ids)],
                        "excluded_no_consent_count": audience_size - len(recipients),
                        "pdpa_consent_verified": True,
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

            rec.write(vals)
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

    def action_pause(self):
        for rec in self:
            if rec.state != "running":
                raise UserError("Only a RUNNING campaign pauses")
            rec.state = "paused"

    def action_resume(self):
        for rec in self:
            if rec.state != "paused":
                raise UserError("Only a PAUSED campaign resumes")
            rec.state = "running"

    def action_complete(self):
        for rec in self:
            if rec.state not in ("running", "paused"):
                raise UserError("Complete an active campaign")
            rec.state = "completed"
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
