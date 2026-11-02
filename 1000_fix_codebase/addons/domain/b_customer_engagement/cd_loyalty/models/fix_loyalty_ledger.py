# fix_loyalty_ledger — M10 Append-Only Points Ledger (CD-M10-01).
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish


class FixLoyaltyLedger(models.Model):
    _name = "fix.loyalty.ledger"
    _description = "Loyalty Points Audit Ledger"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.dofa.mixin"]
    _order = "create_date desc, id desc"

    # REQ-10.3 thresholds, stated in points. The specification's REQ text and
    # its DOFA matrix disagree here (REQ: >500 Tier 2, >2,000 Tier 3; matrix:
    # <=500 Tier 1, <=2,000 Tier 2, <=10,000 Tier 3). The REQ text is what the
    # code has always followed, so it is what is implemented; switching to the
    # matrix is this one list.
    _DOFA_POINT_THRESHOLDS = [
        (500.0, "tier_0"),
        (2000.0, "tier_2"),
        (10000.0, "tier_3"),
        (float("inf"), "tier_4"),
    ]

    def _dofa_amount(self) -> float:
        """Only manual adjustments carry financial authority. An accrual is
        earned and a redemption is already balance-checked."""
        self.ensure_one()
        if self.transaction_type != "adjustment":
            return 0.0
        return abs(self.points or 0)

    def _dofa_thresholds(self):
        return self._DOFA_POINT_THRESHOLDS

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        direction = "credit" if (self.points or 0) >= 0 else "debit"
        return "a manual %s of %d points" % (direction, abs(self.points or 0))

    @api.depends("points", "transaction_type")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

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
        default=lambda self: self.env.ref("base.BDT", raise_if_not_found=False)
        or self.env.company.currency_id,
    )

    expiry_date = fields.Date(
        string="Expiration Date",
        help="Date when these points expire if unredeemed.",
    )
    # Legacy approval fields. Kept so existing records and reports still read,
    # but they no longer gate anything: the audit of 2026-10-31 found a single
    # operator self-approving a 5,000-point credit through is_approved. The
    # authority now lives in fix.dofa.mixin, which checks the approver's group
    # and refuses self-approval.
    is_approved = fields.Boolean(
        string="Supervisor Approved (legacy)", default=False, tracking=True
    )
    approved_by = fields.Many2one("res.users", string="Supervisor (legacy)", readonly=True)
    justification = fields.Char(string="Adjustment Justification", tracking=True)

    # FIFO expiry bookkeeping. Without this flag cron_expire_points re-expired
    # the same accrual on every run, because the source entry still matched its
    # own search (audit 2026-10-31).
    points_expired = fields.Boolean(
        string="Accrual Already Expired",
        default=False,
        readonly=True,
        copy=False,
        index=True,
        help="Set once the FIFO expiry run has consumed this accrual.",
    )
    expiry_warned_days = fields.Integer(
        string="Expiry Warning Sent (days out)",
        default=0,
        readonly=True,
        copy=False,
        help="30 or 7 once the member has been warned at that horizon (REQ-10.2).",
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
        """Post the ledger line, recalculate account balance, and evaluate tier.

        FLAW-10.1: Employs pessimistic row-level locking (SELECT FOR UPDATE) on the loyalty account.
        FLAW-10.3: Enforces supervisor DOFA approval and justification on adjustments > 500 points.
        """
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only draft transactions can be posted.")
            account = rec.account_id
            if account.state != "active":
                raise UserError(
                    f"Cannot post transaction: account {account.name} is {account.state}."
                )

            # REQ-10.3: manual adjustments need real DOFA authority. This covers
            # debits as well as credits — the old gate was `points > 500`, so a
            # 9,000-point manual debit posted unapproved (audit 2026-10-31).
            rec._dofa_assert_approved("Manual point adjustment")

            # FLAW-10.1: Pessimistic row locking on loyalty account to prevent double spending.
            # The raw SELECT FOR UPDATE bypasses the ORM cache — flush pending
            # ORM writes FIRST or the lock reads a stale pre-earn balance (audit
            # 2026-10-31: a redeem immediately after an earn saw 0 points).
            current_balance = account.points_balance
            if rec.points < 0:
                self.env.flush_all()
                self.env.cr.execute(
                    "SELECT points_balance FROM fix_loyalty_account WHERE id = %s FOR UPDATE",
                    (account.id,),
                )
                locked = self.env.cr.fetchone()
                if locked:
                    current_balance = locked[0]

                if (current_balance + rec.points) < 0:
                    raise ValidationError(
                        f"Insufficient points: account has {current_balance} points, "
                        f"attempted to redeem {abs(rec.points)} points (FLAW-10.1)."
                    )

            new_balance = current_balance + rec.points
            rec.balance_after = new_balance

            # Update account lifetime accumulators
            acc_updates = {"points_balance": new_balance}
            if rec.points > 0:
                acc_updates["lifetime_points_earned"] = account.lifetime_points_earned + rec.points
                if rec.order_amount_bdt:
                    acc_updates["lifetime_spend_bdt"] = (
                        account.lifetime_spend_bdt + rec.order_amount_bdt
                    )
            elif rec.points < 0:
                acc_updates["lifetime_points_redeemed"] = account.lifetime_points_redeemed + abs(
                    rec.points
                )

            # Auto-calculate expiration date for accruals (365 days / FIFO)
            if rec.points > 0 and not rec.expiry_date and account.program_id.expiry_months:
                rec.expiry_date = fields.Date.today() + relativedelta(
                    months=account.program_id.expiry_months
                )

            account.write(acc_updates)
            rec.state = "posted"

            # Check tier progression
            account.check_and_update_tier()

            # REQ-10.6: an accrual burst freezes the wallet for investigation.
            if rec.points > 0 and rec.transaction_type == "accrual":
                account._check_velocity_fraud()

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

    @api.model
    def cron_expire_points(self):
        """REQ-10.2: daily FIFO expiry of accruals past their 365-day life.

        Each source accrual is stamped `points_expired` as it is consumed.
        Without that stamp the entry still matched this search on the next run
        and was expired again, draining the member's balance to zero over
        successive days (audit 2026-10-31 — one reason this cron was never
        registered).
        """
        today = fields.Date.today()
        expired_ledgers = self.search(
            [
                ("state", "=", "posted"),
                ("points", ">", 0),
                ("points_expired", "=", False),
                ("expiry_date", "!=", False),
                ("expiry_date", "<=", today),
            ],
            order="expiry_date asc, id asc",  # FIFO: oldest entitlement first
        )
        expired_count = 0
        for entry in expired_ledgers:
            account = entry.account_id
            points_to_expire = min(entry.points, max(account.points_balance, 0))
            if points_to_expire > 0:
                self.create(
                    {
                        "account_id": account.id,
                        "transaction_type": "expiration",
                        "points": -points_to_expire,
                        "notes": f"Automated 365-day point expiration for entry #{entry.id} (IFRS 15)",
                        "state": "draft",
                    }
                ).action_post()
                expired_count += 1
            # Stamped whether or not points were available: the entitlement has
            # lapsed either way and must not be revisited.
            entry.points_expired = True
        return expired_count

    def cron_warn_expiring_points(self):
        """REQ-10.2: notify members 30 and 7 days before their points lapse."""
        today = fields.Date.today()
        warned = 0
        for horizon in (30, 7):
            target = today + relativedelta(days=horizon)
            # Warn once per horizon: 0 means never warned, and a wider horizon
            # already warned (30) still allows the closer one (7).
            due = self.search(
                [
                    ("state", "=", "posted"),
                    ("points", ">", 0),
                    ("points_expired", "=", False),
                    ("expiry_date", "!=", False),
                    ("expiry_date", "<=", target),
                    ("expiry_date", ">", today),
                    "|",
                    ("expiry_warned_days", "=", 0),
                    ("expiry_warned_days", ">", horizon),
                ]
            )
            for entry in due:
                publish(
                    self.env,
                    "loyalty.points_expiring",
                    "fix.loyalty.ledger",
                    entry.id,
                    {
                        "account_no": entry.account_id.name,
                        "partner_id": entry.account_id.partner_id.id,
                        "points": entry.points,
                        "expiry_date": str(entry.expiry_date),
                        "days_remaining": horizon,
                    },
                )
                entry.expiry_warned_days = horizon
                warned += 1
        return warned
