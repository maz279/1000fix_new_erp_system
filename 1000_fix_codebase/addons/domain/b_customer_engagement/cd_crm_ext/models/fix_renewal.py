# fix.renewal — the renewal PIPELINE (M07, FR-CRM-039…043, BRU-CRM-12).
# Renewals are pursuits with value, probability, owner and forecast — not
# reminder lists. Auto-created renewals may be closed but never deleted.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

# A pursuit can be worked (engaged), won or lapsed only while it is live.
LIVE_STATES = ("open", "engaged")


class FixRenewal(models.Model):
    """A renewal pursuit for a contract, membership or warranty product."""

    _name = "fix.renewal"
    _description = "Renewal Pursuit"
    # A03 P2: the outcome is a transition, not a field a user types (G-M07-10).
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
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
            ("engaged", "In Engagement"),
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
    engaged_at = fields.Datetime(string="Engagement Started", readonly=True, copy=False)
    winback_lead_id = fields.Many2one(
        "crm.lead", string="Win-Back Opportunity", readonly=True, copy=False
    )
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )

    def _fix_guarded_fields(self) -> set:
        # auto_created is guarded too: clearing it was a way round the
        # BRU-CRM-12 no-delete rule.
        return super()._fix_guarded_fields() | {
            "state",
            "auto_created",
            "engaged_at",
            "winback_lead_id",
        }

    @api.model
    def action_create_renewals(self, lead_time_days=90):
        """AUT-CRM-05: create renewal pursuits at the configured lead time for
        expiring sources. The M08/M10/M09 contract stores are seams until
        those modules are rebuilt — sources are read opportunistically, and
        the method reports what it found rather than inventing data.

        A03 P2: the lead time was never applied (every contract ending in
        the future got a pursuit at once), and fix.contract names its party
        customer_id, not partner_id, so the first real contract would have
        crashed the run. Both are read from the source model now."""
        today = fields.Date.today()
        created = 0
        for model, source_type in (("fix.contract", "contract"), ("fix.membership", "membership")):
            if model not in self.env:
                continue
            Source = self.env[model].sudo()
            party_field = "customer_id" if "customer_id" in Source._fields else "partner_id"
            domain = [("date_end", ">=", today)]
            if "state" in Source._fields and source_type == "contract":
                domain.append(("state", "in", ("active", "expiring")))
            for contract in Source.search(domain):
                horizon = getattr(contract, "renewal_lead_days", 0) or lead_time_days
                if (contract.date_end - today).days > horizon:
                    continue
                if self.sudo().search_count(
                    [("source_type", "=", source_type), ("source_ref", "=", str(contract.id))]
                ):
                    continue
                self.sudo().create(
                    {
                        "source_type": source_type,
                        "source_ref": str(contract.id),
                        "partner_id": contract[party_field].id,
                        "value": getattr(contract, "annual_value", 0.0)
                        or getattr(contract, "amount_total", 0.0)
                        or 0.0,
                        "expiry_date": contract.date_end,
                        "lead_time_days": (contract.date_end - today).days,
                        "auto_created": True,
                        "company_id": contract.company_id.id or self.env.company.id,
                    }
                )
                created += 1
        return created

    @api.model
    def cron_create_renewals(self):
        """Nightly AUT-CRM-05 run (the method existed with no ir.cron, G-M07-8)."""
        return self.action_create_renewals()

    def _assert_live(self, verb: str) -> None:
        labels = dict(self._fields["state"].selection)
        for renewal in self:
            if renewal.state not in LIVE_STATES:
                raise UserError(
                    "The renewal for %s is %s; only an open renewal can be %s."
                    % (renewal.partner_id.name, labels[renewal.state].lower(), verb)
                )

    def action_engage(self):
        """Start working the renewal play: the owner takes it and gets a to-do
        for the play's first touch. The P03 "Start Engagement" button, which
        called a method that did not exist (A03 audit G-M07-7)."""
        self._assert_live("engaged")
        plays = dict(self._fields["play"].selection)
        for renewal in self.filtered(lambda r: r.state == "open"):
            owner = renewal.owner_id or self.env.user
            renewal._guarded().write(
                {"state": "engaged", "engaged_at": fields.Datetime.now(), "owner_id": owner.id}
            )
            renewal.activity_schedule(
                "mail.mail_activity_data_todo",
                date_deadline=fields.Date.today(),
                summary="Renewal play: %s" % plays.get(renewal.play, renewal.play),
                note="Contact %s about the renewal due %s."
                % (renewal.partner_id.name, renewal.expiry_date),
                user_id=owner.id,
            )
            renewal.message_post(body="Renewal engagement started by %s." % self.env.user.name)
        return True

    def action_renew(self):
        """The renewal was won. The P03 "Mark Renewed" button (G-M07-7)."""
        self._assert_live("renewed")
        for renewal in self:
            renewal._guarded().write({"state": "renewed"})
            publish(
                self.env,
                "renewal.created",
                "fix.renewal",
                renewal.id,
                {"partner_id": renewal.partner_id.id, "outcome": "renewed"},
            )
        return True

    def action_win(self):
        """The original name of action_renew, kept for its callers."""
        return self.action_renew()

    def action_close(self, reason=None):
        """No renewal is possible (the source was terminated, the account
        closed). BRU-CRM-12's "closed, never deleted" outcome, which had no
        action once the state became a guarded field."""
        if not (reason or "").strip():
            raise UserError("Say why no renewal is possible before closing it.")
        self._assert_live("closed")
        for renewal in self:
            renewal._guarded().write({"state": "closed"})
            renewal.message_post(body="Renewal closed, no renewal possible: %s" % reason.strip())
        return True

    def action_lapse(self):
        """Lapse moves the account into the win-back pipeline (FR-CRM-043):
        a lapsed renewal opens a win-back opportunity on crm.lead. Lapsing
        twice opened two win-back deals (G-M07-10); a renewal lapses once."""
        self._assert_live("lapsed")
        Opportunity = self.env["crm.lead"].with_context(default_type="opportunity")
        for renewal in self:
            winback = Opportunity.create(
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
            renewal._guarded().write({"state": "lapsed", "winback_lead_id": winback.id})
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
