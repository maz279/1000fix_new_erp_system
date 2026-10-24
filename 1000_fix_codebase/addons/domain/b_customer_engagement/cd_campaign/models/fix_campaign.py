# fix_campaign — M35: campaigns, attribution, bilingual content (P08-M04-T08, R06-M01-T05).
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

from libs.py.fix_events import publish

# Addressed channels message individual people: each needs a GRANTED
# fix.consent (cd_party_master) on that channel or the all-channel
# "marketing" consent. Social/search/billboard reach no individual recipient.
CHANNEL_CONSENTS = {
    "sms": ("sms", "marketing"),
    "email": ("email", "marketing"),
    "portal": ("push", "marketing"),
}
# Segments whose membership this module can resolve without another module's
# data; any other segment must state its audience_domain explicitly.
SELF_RESOLVED_SEGMENTS = {"all_customers": []}


class FixCampaign(models.Model):
    """Marketing campaigns with audience segmentation, PDPA consent filtering,
    response attribution ledger, and M10 loyalty integration hooks."""

    _name = "fix.campaign"
    _description = "Marketing Campaign"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "start_date desc"

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
        """The segment partners whose LATEST consent decision covering the
        campaign channel is a grant."""
        self.ensure_one()
        consents = self.env["fix.consent"].search(
            [
                ("partner_id", "any", domain),
                ("channel", "in", CHANNEL_CONSENTS[self.channel]),
                ("state", "=", "granted"),
                ("company_id", "in", [self.company_id.id, False]),
            ]
        )
        withdrawn = self.env["fix.consent"].search(
            [
                ("partner_id", "in", consents.partner_id.ids),
                ("channel", "in", CHANNEL_CONSENTS[self.channel]),
                ("state", "in", ("withdrawn", "expired")),
            ]
        )
        latest = {}
        for consent in consents | withdrawn:
            when = consent.date_withdrawn or consent.date_granted or consent.create_date
            key = consent.partner_id.id
            if key not in latest or when > latest[key][0]:
                latest[key] = (when, consent.state)
        # the LATEST decision wins: a later withdrawal revokes an older grant
        return self.env["res.partner"].browse(
            [pid for pid, (_when, state) in latest.items() if state == "granted"]
        )

    @api.depends("response_ids", "budget")
    def _compute_response_count(self):
        for rec in self:
            rec.response_count = len(rec.response_ids)
            rec.cost_per_response = (
                round(rec.budget / len(rec.response_ids), 2) if rec.response_ids else 0.0
            )

    def action_launch(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Launch from draft only")
            if not rec.start_date or not rec.end_date:
                raise UserError("A campaign runs between dates")
            if rec.end_date < rec.start_date:
                raise UserError("Campaign window is inverted")
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
