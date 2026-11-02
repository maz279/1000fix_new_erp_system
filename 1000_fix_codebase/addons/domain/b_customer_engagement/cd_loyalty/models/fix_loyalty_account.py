# fix_loyalty_account — M10 Customer Loyalty Account (CD-M10-01).
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish


class FixLoyaltyAccount(models.Model):
    _name = "fix.loyalty.account"
    _description = "Customer Loyalty Membership Account"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "points_balance desc, create_date desc"

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

    name = fields.Char(
        string="Membership Number",
        required=True,
        readonly=True,
        copy=False,
        default=lambda self: self.env["ir.sequence"].next_by_code("fix.loyalty.account") or "NEW",
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Customer Party",
        required=True,
        ondelete="restrict",
        index=True,
        tracking=True,
    )
    program_id = fields.Many2one(
        "fix.loyalty.program",
        string="Programme",
        required=True,
        ondelete="restrict",
        index=True,
    )
    tier_id = fields.Many2one(
        "fix.loyalty.tier",
        string="Current Tier",
        index=True,
        tracking=True,
    )

    state = fields.Selection(
        [
            ("active", "Active"),
            ("frozen", "Frozen — Fraud Review"),
            ("suspended", "Suspended"),
            ("closed", "Closed"),
        ],
        default="active",
        required=True,
        tracking=True,
    )
    # REQ-10.6 velocity fraud lock
    freeze_reason = fields.Char(string="Freeze Reason", readonly=True, copy=False, tracking=True)
    frozen_at = fields.Datetime(string="Frozen On", readonly=True, copy=False)
    unlock_supervisor_id = fields.Many2one(
        "res.users", string="Unlocked By", readonly=True, copy=False, tracking=True
    )

    points_balance = fields.Integer(
        string="Spendable Points Balance",
        default=0,
        readonly=True,
        tracking=True,
    )
    lifetime_points_earned = fields.Integer(
        string="Lifetime Points Earned",
        default=0,
        readonly=True,
    )
    lifetime_points_redeemed = fields.Integer(
        string="Lifetime Points Redeemed",
        default=0,
        readonly=True,
    )
    lifetime_spend_bdt = fields.Monetary(
        string="Lifetime Spend (BDT)",
        currency_field="currency_id",
        default=0.0,
        readonly=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.ref("base.BDT", raise_if_not_found=False)
        or self.env.company.currency_id,
    )

    enrollment_date = fields.Date(
        string="Enrollment Date",
        default=fields.Date.context_today,
        readonly=True,
    )
    tier_upgraded_date = fields.Date(string="Last Tier Upgrade Date")

    ledger_ids = fields.One2many(
        "fix.loyalty.ledger",
        "account_id",
        string="Points Transactions",
    )
    voucher_ids = fields.One2many(
        "fix.loyalty.voucher",
        "account_id",
        string="Issued Vouchers",
    )

    _partner_prog_unique = models.Constraint(
        "UNIQUE (partner_id, program_id)",
        "Customer already has an active account in this loyalty programme.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("tier_id") and vals.get("program_id"):
                # Assign lowest qualification tier initially
                initial_tier = self.env["fix.loyalty.tier"].search(
                    [("program_id", "=", vals["program_id"]), ("active", "=", True)],
                    order="min_points_threshold asc, sequence asc",
                    limit=1,
                )
                if initial_tier:
                    vals["tier_id"] = initial_tier.id
        records = super().create(vals_list)
        for rec in records:
            publish(
                self.env,
                "loyalty.account_created",
                "fix.loyalty.account",
                rec.id,
                {
                    "account_no": rec.name,
                    "partner_id": rec.partner_id.id,
                    "program": rec.program_id.code,
                    "tier": rec.tier_id.code if rec.tier_id else "NONE",
                },
            )
        return records

    def check_and_update_tier(self):
        """Evaluate qualification thresholds and upgrade tier if earned."""
        self.ensure_one()
        tiers = self.env["fix.loyalty.tier"].search(
            [("program_id", "=", self.program_id.id), ("active", "=", True)],
            order="min_points_threshold desc, min_spend_bdt desc",
        )
        for candidate_tier in tiers:
            meets_points = self.lifetime_points_earned >= candidate_tier.min_points_threshold
            meets_spend = self.lifetime_spend_bdt >= candidate_tier.min_spend_bdt
            if meets_points or meets_spend:
                if self.tier_id != candidate_tier:
                    old_tier = self.tier_id.name if self.tier_id else "None"
                    self.write(
                        {
                            "tier_id": candidate_tier.id,
                            "tier_upgraded_date": fields.Date.today(),
                        }
                    )
                    self.message_post(
                        body=f"Congratulations! Upgraded from {old_tier} to {candidate_tier.name} tier."
                    )
                    publish(
                        self.env,
                        "loyalty.tier_upgraded",
                        "fix.loyalty.account",
                        self.id,
                        {
                            "partner_id": self.partner_id.id,
                            "account_no": self.name,
                            "old_tier": old_tier,
                            "new_tier": candidate_tier.code,
                        },
                    )
                break

    def action_suspend(self):
        self.write({"state": "suspended"})

    def action_activate(self):
        self.write({"state": "active"})

    def action_close(self):
        self.write({"state": "closed"})

    # --- REQ-10.6 velocity fraud detection -------------------------------
    # "more than 3 earn transactions from disparate physical branches within
    # 120 minutes" freezes the wallet for investigation.
    _FRAUD_WINDOW_MINUTES = 120
    _FRAUD_MAX_ACCRUALS = 3

    def _check_velocity_fraud(self):
        """Freeze the wallet when accrual velocity crosses the REQ-10.6 limit."""
        window_start = fields.Datetime.now() - timedelta(minutes=self._FRAUD_WINDOW_MINUTES)
        for account in self:
            if account.state != "active":
                continue
            recent = self.env["fix.loyalty.ledger"].search(
                [
                    ("account_id", "=", account.id),
                    ("transaction_type", "=", "accrual"),
                    ("state", "=", "posted"),
                    ("create_date", ">=", window_start),
                ]
            )
            if len(recent) <= self._FRAUD_MAX_ACCRUALS:
                continue
            # Disparate branches are the stronger signal, but a burst from one
            # till is still a burst: the count alone trips the lock, and the
            # branch spread is recorded for the investigator.
            units = {r.operating_unit_id.id for r in recent if r.operating_unit_id}
            account.write(
                {
                    "state": "frozen",
                    "frozen_at": fields.Datetime.now(),
                    "freeze_reason": (
                        "Velocity check: %d accruals within %d minutes across %d "
                        "operating unit(s) (REQ-10.6)."
                        % (len(recent), self._FRAUD_WINDOW_MINUTES, len(units) or 1)
                    ),
                }
            )
            publish(
                self.env,
                "loyalty.wallet_frozen",
                "fix.loyalty.account",
                account.id,
                {
                    "account_no": account.name,
                    "partner_id": account.partner_id.id,
                    "accruals_in_window": len(recent),
                    "operating_units": len(units),
                },
            )

    def action_unfreeze(self):
        """Release a fraud lock. Tier 2 authority, and never the account owner."""
        for account in self:
            if account.state != "frozen":
                raise UserError("Only a frozen wallet can be released.")
            if not self.env.user.has_group("cd_entity_config.group_dofa_tier_2"):
                raise UserError(
                    "Releasing a fraud lock requires DOFA Tier 2 (Branch / "
                    "Operations Manager) authority."
                )
            account.write(
                {
                    "state": "active",
                    "unlock_supervisor_id": self.env.user.id,
                    "freeze_reason": False,
                    "frozen_at": False,
                }
            )
            account.message_post(
                body="Fraud lock released by %s after investigation." % self.env.user.name
            )
