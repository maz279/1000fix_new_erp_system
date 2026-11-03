# fix_loyalty_ledger — M10 Append-Only Points Ledger (CD-M10-01).
import logging

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

_logger = logging.getLogger(__name__)


class FixLoyaltyLedger(models.Model):
    _name = "fix.loyalty.ledger"
    _description = "Loyalty Points Audit Ledger"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.dofa.mixin"]

    # A03 audit R7: a metered adjustment is approved from the M63 inbox.
    _approval_domain = "loyalty_adjustment"
    _approval_routed = True
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
        """Manual adjustments, and manual credits of any type, carry authority.

        Only 'adjustment' used to count, so a plain user posted a 1,000,000
        point 'accrual' and a 50,000 point 'campaign_bonus' with no approval
        (A03 audit). Lines raised by a system path (campaign hook, expiry,
        redemption) are flagged system_generated and are governed where that
        path is configured. A redemption is already balance-checked."""
        self.ensure_one()
        if self.transaction_type == "adjustment":
            return abs(self.points or 0)
        # Any credit a person keys in mints points, whatever type it is
        # labelled: a positive 'redemption' line used to post at tier_0.
        # System earn paths (closed-order accrual, referral award, campaign
        # hook, merge transfer) are flagged system_generated and stay out.
        if (self.points or 0) > 0 and not self.system_generated:
            return self.points
        return 0.0

    def _dofa_thresholds(self):
        return self._DOFA_POINT_THRESHOLDS

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        direction = "credit" if (self.points or 0) >= 0 else "debit"
        return "a manual %s of %d points" % (direction, abs(self.points or 0))

    @api.depends("points", "transaction_type", "system_generated")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    # A posted line is the record of what happened. Corrections are new,
    # reversing lines; editing the old one rewrites history.
    _POSTED_IMMUTABLE = (
        "account_id",
        "partner_id",
        "transaction_type",
        "points",
        "service_order_id",
        "order_amount_bdt",
        "expiry_date",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "balance_after",
            "system_generated",
            "points_expired",
            "is_approved",
            "approved_by",
            "reversal_of_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state == "posted":
            return locked | set(self._POSTED_IMMUTABLE)
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        # Superuser code is a system path (data loading, crons, service
        # calls), the same trust the field guard extends to it. A person
        # keying in points is never superuser, so their credits stay metered.
        if self.env.su:
            for vals in vals_list:
                vals.setdefault("system_generated", True)
        return super().create(vals_list)

    def write(self, vals):
        if (
            not self._fix_guard_open()
            and set(vals) & set(self._POSTED_IMMUTABLE)
            and any(rec.state == "posted" for rec in self)
        ):
            raise UserError(
                "A posted loyalty ledger line cannot be edited. Reverse it instead "
                "(Reverse Line), so the correction is on the record."
            )
        return super().write(vals)

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
            ("merge_transfer", "Party Merge Transfer"),
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
    reversal_of_id = fields.Many2one(
        "fix.loyalty.ledger",
        string="Reverses",
        readonly=True,
        copy=False,
        index=True,
        help="The posted line this line corrects. Set only by Reverse.",
    )
    system_generated = fields.Boolean(
        readonly=True,
        copy=False,
        help="Raised by a system path (campaign hook, expiry, redemption), not "
        "keyed in by a person. Only those paths can set it.",
    )

    @api.constrains("transaction_type", "points", "system_generated")
    def _check_type_direction(self):
        for rec in self:
            # A positive 'redemption' or 'expiration' is a credit wearing a
            # debit's label; it would also read as negative breakage.
            if rec.transaction_type in ("redemption", "expiration") and rec.points > 0:
                raise ValidationError(
                    "A %s line removes points, so its points must be negative or zero."
                    % dict(self._fields["transaction_type"].selection)[rec.transaction_type]
                )
            # Only the party-merge consumer moves a balance between members.
            if rec.transaction_type == "merge_transfer" and not rec.system_generated:
                raise ValidationError(
                    "A party merge transfer is raised by the merge itself, not keyed in. "
                    "Use a Customer Care Adjustment for a manual correction."
                )

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
            posting = rec._guarded()
            posting.write({"balance_after": new_balance})

            # Update account lifetime accumulators. points_balance is not
            # among them: it is derived from the posted lines (A03 audit
            # M10-2), so marking this line posted is what moves it.
            acc_updates = {}
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
                posting.write(
                    {
                        "expiry_date": fields.Date.today()
                        + relativedelta(months=account.program_id.expiry_months)
                    }
                )

            if acc_updates:
                account._guarded().write(acc_updates)
            posting.write({"state": "posted"})
            if rec.reversal_of_id:
                # The original stays as it was posted; it is marked, not
                # rewritten. An accrual taken back must not lapse later too.
                rec.reversal_of_id._guarded().write({"state": "reversed", "points_expired": True})

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

    def action_reverse(self, reason=None):
        """Correct a posted line by posting its opposite (REQ-10.3).

        A posted line is never edited: the correction is a new draft line for
        the negated points, linked to the original. It is a manual adjustment,
        so above the DOFA threshold a second person approves it before it can
        post, and posting it marks the original 'reversed'. Returns the draft.
        """
        self.ensure_one()
        if not (reason or "").strip():
            raise UserError("State why this line is being reversed.")
        if self.state != "posted":
            raise UserError("Only a posted line can be reversed; edit or delete a draft instead.")
        if self.reversal_of_id:
            raise UserError(
                "This line is itself a reversal. Post a new line rather than reversing a reversal."
            )
        if self.transaction_type != "expiration" and self.points_expired:
            raise UserError(
                "These points already lapsed through expiry. Reverse the expiration line instead."
            )
        open_reversal = self.search([("reversal_of_id", "=", self.id), ("state", "!=", "reversed")])
        if open_reversal:
            raise UserError(
                "Line %s already has a reversal (%s)." % (self.id, open_reversal[0].state)
            )
        reversal = self._guarded().create(
            {
                "account_id": self.account_id.id,
                "transaction_type": "adjustment",
                "points": -self.points,
                "service_order_id": self.service_order_id.id,
                "reversal_of_id": self.id,
                "justification": reason.strip(),
                "notes": "Reversal of ledger line %s: %s" % (self.id, reason.strip()),
                "state": "draft",
            }
        )
        self.message_post(body="Reversal raised as line %s: %s" % (reversal.id, reason.strip()))
        return {"reversal_id": reversal.id}

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
                # A closed account (a merged party's, say) holds nothing to
                # expire; its balance was moved or written off on closing.
                ("account_id.state", "!=", "closed"),
            ],
            order="expiry_date asc, id asc",  # FIFO: oldest entitlement first
        )
        expired_count = 0
        accounts = expired_ledgers.mapped("account_id")
        for account in accounts:
            entries = expired_ledgers.filtered(lambda e, a=account: e.account_id == a)
            # One account per savepoint. A frozen wallet refuses the posting,
            # and that UserError used to abort the whole run, so no member's
            # points expired until the freeze was lifted (A03 audit M10-7).
            # The failed account's entries stay unstamped and retry tomorrow.
            try:
                with self.env.cr.savepoint():
                    expired_count += entries._expire_entries()
            except Exception as exc:  # one broken account must not stop the others
                _logger.warning(
                    "Loyalty expiry skipped account %s (%s): %s", account.name, account.state, exc
                )
        return expired_count

    def _expire_entries(self) -> int:
        """Post the expiration lines for these lapsed accruals of ONE account."""
        expired = 0
        for entry in self.sorted(lambda e: (e.expiry_date, e.id)):
            account = entry.account_id
            points_to_expire = min(entry.points, max(account.points_balance, 0))
            if points_to_expire > 0:
                self._guarded().create(
                    {
                        "system_generated": True,
                        "account_id": account.id,
                        "transaction_type": "expiration",
                        "points": -points_to_expire,
                        "notes": f"Automated 365-day point expiration for entry #{entry.id} (IFRS 15)",
                        "state": "draft",
                    }
                ).action_post()
                expired += 1
            # Stamped whether or not points were available: the entitlement has
            # lapsed either way and must not be revisited.
            entry._guarded().write({"points_expired": True})
        return expired

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
