# cd_entity_config — the Stamp Act 1899 Schedule I rate table.
#
# The A04 audit left "which article applies, and above what value" as an open
# item: the article is now derived from the instrument, but the VALUE
# thresholds were still a matter of someone knowing them.
#
# Encoding a rate in Python would be the wrong fix. Schedule I rates and
# exemption floors move with each Finance Act, and a number compiled into a
# model is a number nobody re-reads. This makes them effective-dated
# CONFIGURATION that Finance or Legal maintain, and makes the system's
# behaviour explicit when no schedule has been entered:
#
#   no schedule row covers the instrument  ->  duty is REQUIRED
#
# That is the conservative position: the system never waives duty because a
# table was left empty.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class FixStampDutySchedule(models.Model):
    """One effective-dated Schedule I head: its rate and its exemption floor."""

    _name = "fix.stamp.duty.schedule"
    _description = "Stamp Act 1899 Schedule I Rate"
    _inherit = ["mail.thread"]
    _order = "article, date_from desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    article = fields.Selection(
        [
            ("art_5", "Article 5 - Agreement / Memorandum"),
            ("art_15", "Article 15 - Bond / Guarantee"),
            ("art_35", "Article 35 - Lease / Hire"),
        ],
        string="Schedule I Article",
        required=True,
        index=True,
        tracking=True,
    )
    name = fields.Char(
        string="Description",
        required=True,
        help="How this row reads in the Act, in the maintainer's own words.",
    )
    date_from = fields.Date(
        string="Effective From",
        required=True,
        tracking=True,
        help="The Finance Act date this rate took effect.",
    )
    date_to = fields.Date(
        string="Effective To",
        tracking=True,
        help="Left empty while the rate is current.",
    )
    exemption_floor_bdt = fields.Monetary(
        string="Duty-Free Threshold",
        currency_field="currency_id",
        help="Instruments at or below this value are not chargeable under this "
        "article. Zero means every instrument is chargeable.",
    )
    duty_rate_pct = fields.Float(
        string="Ad Valorem Rate (%)",
        help="Where the head is charged as a percentage of value.",
    )
    duty_fixed_bdt = fields.Monetary(
        string="Fixed Duty",
        currency_field="currency_id",
        help="Where the head carries a fixed duty rather than a rate.",
    )
    statutory_reference = fields.Char(
        string="Statutory Reference",
        help="The Finance Act or SRO this row is taken from, so a reader can "
        "check it rather than trust it.",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    state = fields.Selection(
        [("draft", "Draft - not in force"), ("confirmed", "Confirmed by Finance")],
        default="draft",
        required=True,
        index=True,
        tracking=True,
        help="A draft row NEVER takes effect. Until Finance confirms a row "
        "against the current Finance Act, the instrument stays chargeable - "
        "the system does not waive duty on an unverified number.",
    )
    confirmed_by = fields.Many2one("res.users", readonly=True, tracking=True)
    confirmed_on = fields.Datetime(readonly=True, tracking=True)
    active = fields.Boolean(default=True)

    def action_confirm(self):
        """Finance stands behind this row, by name and date."""
        for rec in self:
            if rec.state == "confirmed":
                raise UserError("This rate row is already confirmed.")
            if not (rec.statutory_reference or "").strip():
                raise UserError(
                    "Cite the Finance Act or SRO this rate comes from before "
                    "confirming it: a rate nobody can check is not a rate."
                )
            rec.write(
                {
                    "state": "confirmed",
                    "confirmed_by": self.env.user.id,
                    "confirmed_on": fields.Datetime.now(),
                }
            )
            rec.message_post(
                body="Schedule I rate confirmed by %s against %s."
                % (self.env.user.name, rec.statutory_reference)
            )
        return True

    def action_reset_to_draft(self):
        """Withdraw a rate - it stops being in force immediately."""
        for rec in self:
            rec.write({"state": "draft", "confirmed_by": False, "confirmed_on": False})
            rec.message_post(body="Rate withdrawn by %s." % self.env.user.name)
        return True

    @api.constrains("date_from", "date_to")
    def _check_window(self):
        for rec in self:
            if rec.date_to and rec.date_to < rec.date_from:
                raise ValidationError(
                    "The effective-to date cannot precede the effective-from date."
                )

    @api.model
    def rate_for(self, article, on_date=None, company=None):
        """The row IN FORCE for an article on a date, or an empty recordset.

        Only a CONFIRMED row is in force. A draft is someone's working note;
        treating it as law would let an unchecked number waive duty.

        `context_today`, not UTC `today`: Bangladesh is UTC+6, so for the first
        six hours of each local day UTC is still on the previous date - and a
        Finance Act commences on a date, so the wrong side of that boundary
        selects the wrong rate.
        """
        on_date = on_date or fields.Date.context_today(self)
        company = company or self.env.company
        return self.search(
            [
                ("article", "=", article),
                ("company_id", "=", company.id),
                ("state", "=", "confirmed"),
                ("date_from", "<=", on_date),
                "|",
                ("date_to", "=", False),
                ("date_to", ">=", on_date),
            ],
            limit=1,
        )

    @api.model
    def is_chargeable(self, article, amount, on_date=None, company=None):
        """Whether an instrument of this value is chargeable under this head.

        Returns True when no schedule row covers it: an unmaintained table
        must not silently waive duty.
        """
        row = self.rate_for(article, on_date=on_date, company=company)
        if not row:
            return True
        return (amount or 0.0) > (row.exemption_floor_bdt or 0.0)
