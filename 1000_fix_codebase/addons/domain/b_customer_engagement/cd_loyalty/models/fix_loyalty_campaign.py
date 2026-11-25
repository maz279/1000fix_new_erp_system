# fix_loyalty_campaign — M10 Campaign Integration Hooks (CD-M10-01).
from dateutil.relativedelta import relativedelta
from odoo import fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish


class FixLoyaltyCampaignHook(models.Model):
    _name = "fix.loyalty.campaign.hook"
    _description = "Loyalty Campaign Integration Hook"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]

    # A03 audit M10-8 (R5): the hook's state was an editable form field and the
    # hook had no transitions, so a hook was "activated" - and started minting
    # campaign points and vouchers - by typing the state. It now moves only
    # through action_activate / action_complete, and the reward terms freeze
    # once it is live so a running hook cannot be re-priced.
    _REWARD_TERMS = frozenset(
        {
            "campaign_id",
            "program_id",
            "reward_type",
            "bonus_points",
            "voucher_discount_type",
            "voucher_discount_value",
            "voucher_validity_days",
        }
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(rec.state != "draft" for rec in self):
            locked |= self._REWARD_TERMS
        return locked

    def write(self, vals):
        if not self._fix_guard_open() and self._REWARD_TERMS & set(vals):
            live = self.filtered(lambda r: r.state != "draft")
            if live:
                raise UserError(
                    "Campaign hook %s is %s: its reward terms are fixed. Complete it and "
                    "create a new hook to change the reward."
                    % (
                        ", ".join(live.mapped("name")),
                        dict(self._fields["state"].selection)[live[0].state],
                    )
                )
        return super().write(vals)

    def action_activate(self):
        """Go live: the campaign must be running and the reward must be real."""
        for hook in self:
            if hook.state != "draft":
                raise UserError("Only a draft campaign hook can be activated.")
            if hook.campaign_id.state != "running":
                raise UserError(
                    "Campaign %s is not running: a hook only goes live on a running, "
                    "budget-approved campaign." % hook.campaign_id.display_name
                )
            if hook.reward_type == "voucher":
                if not (hook.voucher_discount_value > 0 and hook.voucher_validity_days > 0):
                    raise UserError("A voucher hook needs a positive discount and validity.")
            elif hook.bonus_points <= 0:
                raise UserError("A points hook needs a positive bonus.")
            hook._guarded().write({"state": "active"})
            hook.message_post(body="Campaign hook activated by %s." % self.env.user.name)
        return True

    def action_complete(self):
        for hook in self:
            if hook.state != "active":
                raise UserError("Only an active campaign hook can be completed.")
            hook._guarded().write({"state": "completed"})
            hook.message_post(body="Campaign hook completed by %s." % self.env.user.name)
        return True

    _order = "create_date desc"

    # AS-03: Company and Operating Unit scoping
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Operating Unit",
        index=True,
    )

    name = fields.Char(string="Hook Description", required=True)
    campaign_id = fields.Many2one(
        "fix.campaign",
        string="Marketing Campaign",
        required=True,
        index=True,
    )
    program_id = fields.Many2one(
        "fix.loyalty.program",
        string="Target Programme",
        required=True,
        index=True,
    )
    reward_type = fields.Selection(
        [
            ("bonus_points", "Bonus Points Grant"),
            ("voucher", "Promotional Voucher Issuance"),
        ],
        string="Reward Type",
        default="bonus_points",
        required=True,
    )

    bonus_points = fields.Integer(
        string="Bonus Points Amount",
        default=100,
        help="Points awarded to each qualifying campaign responder.",
    )
    voucher_discount_type = fields.Selection(
        [("fixed_bdt", "Fixed BDT"), ("percentage", "Percentage (%)")],
        string="Voucher Discount Type",
        default="fixed_bdt",
    )
    voucher_discount_value = fields.Float(
        string="Voucher Discount Value",
        default=200.0,
    )
    voucher_validity_days = fields.Integer(
        string="Voucher Validity (Days)",
        default=30,
    )

    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("completed", "Completed")],
        default="draft",
        required=True,
        tracking=True,
    )

    def action_execute_campaign_rewards(self, partner_ids):
        """Execute promotional rewards for a list of participating customer partners."""
        self.ensure_one()
        if self.state != "active":
            raise UserError("Only active loyalty campaign hooks can disburse rewards.")

        rewarded_count = 0
        for partner in partner_ids:
            account = self.env["fix.loyalty.account"].search(
                [
                    ("partner_id", "=", partner.id),
                    ("program_id", "=", self.program_id.id),
                    ("state", "=", "active"),
                ],
                limit=1,
            )

            if not account:
                # Auto-enroll in program if not already enrolled
                account = self.env["fix.loyalty.account"].create(
                    {
                        "partner_id": partner.id,
                        "program_id": self.program_id.id,
                        "company_id": self.company_id.id,
                    }
                )

            if self.reward_type == "bonus_points" and self.bonus_points > 0:
                # system_generated: the hook's own configuration is what
                # authorises the bonus, not a person keying in points.
                ledger = (
                    self.env["fix.loyalty.ledger"]
                    ._guarded()
                    .create(
                        {
                            "system_generated": True,
                            "account_id": account.id,
                            "transaction_type": "campaign_bonus",
                            "points": self.bonus_points,
                            "notes": f"Campaign bonus: {self.campaign_id.name}",
                            "company_id": self.company_id.id,
                        }
                    )
                )
                ledger.action_post()
                rewarded_count += 1
            elif self.reward_type == "voucher":
                today = fields.Date.today()
                self.env["fix.loyalty.voucher"].create(
                    {
                        "account_id": account.id,
                        "partner_id": partner.id,
                        "campaign_id": self.campaign_id.id,
                        "discount_type": self.voucher_discount_type,
                        "discount_value": self.voucher_discount_value,
                        "valid_from": today,
                        "valid_until": today + relativedelta(days=self.voucher_validity_days),
                        "state": "active",
                        "company_id": self.company_id.id,
                    }
                )
                rewarded_count += 1

        publish(
            self.env,
            "loyalty.campaign_rewards_disbursed",
            "fix.loyalty.campaign.hook",
            self.id,
            {
                "hook_id": self.id,
                "campaign_id": self.campaign_id.id,
                "reward_type": self.reward_type,
                "rewarded_count": rewarded_count,
            },
        )
        return rewarded_count
