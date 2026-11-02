# fix.renewal — the renewal PIPELINE (M07, FR-CRM-039…043, BRU-CRM-12).
# Renewals are pursuits with value, probability, owner and forecast — not
# reminder lists. Auto-created renewals may be closed but never deleted.
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FixRenewal(models.Model):
    """A renewal pursuit for a contract, membership or warranty product."""

    _name = "fix.renewal"
    _description = "Renewal Pursuit"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "expiry_date, id"

    source_type = fields.Selection(
        [
            ("contract", "Contract (M08)"),
            ("membership", "Membership (M10)"),
            ("warranty", "Warranty Product (M09)"),
        ],
        string="Source Type",
        required=True,
        tracking=True,
    )
    source_ref = fields.Char(string="Source Reference")
    partner_id = fields.Many2one(
        "res.partner", string="Account", required=True, index=True, ondelete="cascade"
    )
    value = fields.Monetary(string="Renewal Value", default=0.0)
    currency_id = fields.Many2one(
        "res.currency", string="Currency", default=lambda self: self.env.company.currency_id
    )
    expiry_date = fields.Date(string="Expiry Date", required=True)
    lead_time_days = fields.Integer(
        string="Created Lead Time (days)",
        readonly=True,
        help="How far before expiry this pursuit was created (Q-06 open with CCO)",
    )
    risk_band = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        string="Risk Band",
        default="medium",
        tracking=True,
        help="Scored from utilisation, satisfaction, SLA attainment, incidents, "
        "engagement (FR-CRM-041; source signals arrive with M34/M05)",
    )
    play = fields.Selection(
        [
            ("auto_renew", "Automatic Renewal (low)"),
            ("light_touch", "Light Touch (medium)"),
            ("executive", "Executive Engagement (high)"),
        ],
        string="Renewal Play",
        default="light_touch",
        tracking=True,
    )
    owner_id = fields.Many2one("res.users", string="Owner", default=lambda self: self.env.user)
    state = fields.Selection(
        [
            ("open", "Open"),
            ("renewed", "Renewed"),
            ("lapsed", "Lapsed"),
            ("closed", "Closed (no renewal possible)"),
        ],
        string="State",
        default="open",
        required=True,
        tracking=True,
    )
    auto_created = fields.Boolean(string="Auto-Created", readonly=True, default=False)
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )

    @api.model
    def action_create_renewals(self, lead_time_days=90):
        """AUT-CRM-05: create renewal pursuits at the configured lead time for
        expiring sources. The M08/M10/M09 contract stores are seams until
        those modules are rebuilt — sources are read opportunistically, and
        the method reports what it found rather than inventing data."""
        today = fields.Date.today()
        created = 0
        # M08 contracts: cd_billing_engine's AR world carries no contract
        # store yet (M08 rebuild pending) — the AMC contract model, when it
        # lands, plugs in here. Nothing is fabricated meanwhile.
        for model, source_type in (("fix.contract", "contract"), ("fix.membership", "membership")):
            if model in self.env:
                for contract in self.env[model].search([("date_end", ">=", today)]):
                    if self.search_count(
                        [("source_type", "=", source_type), ("source_ref", "=", contract.id)]
                    ):
                        continue
                    self.create(
                        {
                            "source_type": source_type,
                            "source_ref": str(contract.id),
                            "partner_id": contract.partner_id.id,
                            "value": getattr(contract, "amount_total", 0.0) or 0.0,
                            "expiry_date": contract.date_end,
                            "lead_time_days": (contract.date_end - today).days,
                            "auto_created": True,
                        }
                    )
                    created += 1
        return created

    def action_win(self):
        for renewal in self:
            renewal.state = "renewed"
            from libs.py.fix_events import publish

            publish(
                self.env,
                "renewal.created",
                "fix.renewal",
                renewal.id,
                {"partner_id": renewal.partner_id.id, "outcome": "renewed"},
            )
        return True

    def action_lapse(self):
        """Lapse moves the account into the win-back pipeline (FR-CRM-043):
        a lapsed renewal opens a win-back opportunity on crm.lead."""
        Opportunity = self.env["crm.lead"].with_context(default_type="opportunity")
        for renewal in self:
            renewal.state = "lapsed"
            Opportunity.create(
                {
                    "name": "Win-back: %s" % renewal.partner_id.name,
                    "partner_id": renewal.partner_id.id,
                    "type": "opportunity",
                    "pipeline_id": self.env["fix.pipeline"]
                    .search([("revenue_stream", "=", "winback")], limit=1)
                    .id,
                    "user_id": renewal.owner_id.id,
                }
            )
            from libs.py.fix_events import publish

            publish(
                self.env,
                "renewal.lost",
                "fix.renewal",
                renewal.id,
                {"partner_id": renewal.partner_id.id},
            )
        return True

    def unlink(self):
        # BRU-CRM-12: an auto-created renewal may be closed but not deleted.
        if any(r.auto_created for r in self):
            raise ValidationError(
                "An automatically created renewal may be closed but never " "deleted (BRU-CRM-12)"
            )
        return super().unlink()
