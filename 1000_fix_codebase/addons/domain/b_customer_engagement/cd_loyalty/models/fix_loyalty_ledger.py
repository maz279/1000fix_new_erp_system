# fix_loyalty_ledger — M10 Append-Only Points Ledger (CD-M10-01).
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish


class FixLoyaltyLedger(models.Model):
    _name = "fix.loyalty.ledger"
    _description = "Loyalty Points Audit Ledger"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc, id desc"

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

    account_id = fields.Many2one(
        "fix.loyalty.account",
        string="Loyalty Account",
        required=True,
        ondelete="restrict",
        index=True,
    )
    partner_id = fields.Many2one(
        related="account_id.partner_id",
        string="Customer Party",
        store=True,
        index=True,
    )
    transaction_type = fields.Selection(
        [
            ("accrual", "Service Accrual"),
            ("redemption", "Voucher / Bill Redemption"),
            ("adjustment", "Customer Care Adjustment"),
            ("referral_bonus", "Referral Reward"),
            ("campaign_bonus", "Campaign Promotion"),
            ("expiration", "Points Expiration"),
        ],
        string="Transaction Type",
        required=True,
        index=True,
    )

    points = fields.Integer(
        string="Points Amount",
        required=True,
        help="Signed point quantity: positive for accruals, negative for redemptions.",
    )
    balance_after = fields.Integer(
        string="Balance After Transaction",
        readonly=True,
        help="Snapshot of spendable points balance after posting.",
    )

    # Reference documents
    service_order_id = fields.Many2one(
        "fix.service.order",
        string="Service Order Reference",
        index=True,
        help="Linked repair order generating or redeeming points.",
    )
    order_amount_bdt = fields.Monetary(
        string="Order Amount (BDT)",
        currency_field="currency_id",
        help="Underlying commercial invoice/estimate amount.",
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.ref("base.BDT", raise_if_not_found=False) or self.env.company.currency_id,
    )

    expiry_date = fields.Date(
        string="Expiration Date",
        help="Date when these points expire if unredeemed.",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("posted", "Posted"),
            ("reversed", "Reversed"),
        ],
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )
    notes = fields.Text(string="Reason / Narration")

    def action_post(self):
        """Post the ledger line, recalculate account balance, and evaluate tier."""
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only draft transactions can be posted.")
            account = rec.account_id
            if account.state != "active":
                raise UserError(f"Cannot post transaction: account {account.name} is {account.state}.")

            # Validate sufficient points on redemption
            if rec.points < 0 and (account.points_balance + rec.points) < 0:
                raise ValidationError(
                    f"Insufficient points: account has {account.points_balance} points, "
                    f"attempted to redeem {abs(rec.points)} points."
                )

            new_balance = account.points_balance + rec.points
            rec.balance_after = new_balance

            # Update account lifetime accumulators
            acc_updates = {"points_balance": new_balance}
            if rec.points > 0:
                acc_updates["lifetime_points_earned"] = account.lifetime_points_earned + rec.points
                if rec.order_amount_bdt:
                    acc_updates["lifetime_spend_bdt"] = account.lifetime_spend_bdt + rec.order_amount_bdt
            elif rec.points < 0:
                acc_updates["lifetime_points_redeemed"] = account.lifetime_points_redeemed + abs(rec.points)

            # Auto-calculate expiration date for accruals
            if rec.points > 0 and not rec.expiry_date and account.program_id.expiry_months:
                rec.expiry_date = fields.Date.today() + relativedelta(months=account.program_id.expiry_months)

            account.write(acc_updates)
            rec.state = "posted"

            # Check tier progression
            account.check_and_update_tier()

            # Emit audit event
            event_name = "loyalty.points_accrued" if rec.points > 0 else "loyalty.points_redeemed"
            publish(
                self.env,
                event_name,
                "fix.loyalty.ledger",
                rec.id,
                {
                    "account_no": account.name,
                    "partner_id": account.partner_id.id,
                    "points": rec.points,
                    "balance_after": new_balance,
                    "type": rec.transaction_type,
                    "service_order": rec.service_order_id.name if rec.service_order_id else False,
                },
            )
