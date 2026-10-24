# fix_loyalty_campaign — M10 Campaign Integration Hooks (CD-M10-01).
from dateutil.relativedelta import relativedelta
from odoo import fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish


class FixLoyaltyCampaignHook(models.Model):
    _name = "fix.loyalty.campaign.hook"
    _description = "Loyalty Campaign Integration Hook"
    _inherit = ["mail.thread", "mail.activity.mixin"]
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
                ledger = self.env["fix.loyalty.ledger"].create(
                    {
                        "account_id": account.id,
                        "transaction_type": "campaign_bonus",
                        "points": self.bonus_points,
                        "notes": f"Campaign bonus: {self.campaign_id.name}",
                        "company_id": self.company_id.id,
                    }
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

    def action_activate(self):
        self.write({"state": "active"})
