# M10 — the scheme EVALUATOR, plus the account-side changes the scheme needs:
# a qualifying-point balance, affiliation membership, tier requalification and
# the loyalty card.
#
# Kept separate from fix_loyalty_scheme.py (which defines the rule records)
# because this file is where the DECISIONS are taken, and those are the lines
# anyone auditing an earn figure needs to read.
#
# The two-balance change is the one with teeth. `points_balance` stays exactly
# what it was — the spendable balance and the IFRS-15 liability — and
# `qualifying_points_balance` is new, counts toward tier, and can never be
# spent. Before this they were one number, so a campaign that accelerated tier
# progress unavoidably inflated the redemption liability. Finance and
# marketing were sharing a field and neither knew it.
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28


class FixLoyaltyProgramSchemes(models.Model):
    """Attach schemes and the tier-retention window to the programme."""

    _inherit = "fix.loyalty.program"

    scheme_ids = fields.One2many("fix.loyalty.scheme", "program_id", string="Schemes")
    point_type_ids = fields.One2many("fix.loyalty.point.type", "program_id", string="Point Types")
    affiliation_ids = fields.One2many(
        "fix.loyalty.affiliation", "program_id", string="Affiliations"
    )
    tier_retention_months = fields.Integer(
        string="Tier Retention (months)",
        default=0,
        help="How long a member keeps a tier after reaching it. Microsoft "
        "states tier retention as a duration; the estate had a lifetime "
        "threshold, so a tier could only ever go up. 0 keeps the old "
        "lifetime behaviour, which is a real policy and not a disabled "
        "feature.",
    )

    @api.constrains("tier_retention_months")
    def _check_retention(self):
        for rec in self:
            if rec.tier_retention_months < 0:
                raise ValidationError("Tier retention cannot be negative.")

    def active_scheme(self, on_date=None):
        """The live scheme for this programme, lowest sequence first.

        Returns an empty recordset when none is live, and every caller treats
        that as "fall back to points_per_bdt" rather than "earn nothing" —
        introducing schemes must not silently stop the existing programme.
        """
        self.ensure_one()
        for scheme in self.scheme_ids.sorted(lambda s: (s.sequence, s.id)):
            if scheme.is_live(on_date):
                return scheme
        return self.env["fix.loyalty.scheme"]


class FixLoyaltyCard(models.Model):
    """A physical or wallet card identifying a member at the counter."""

    _name = "fix.loyalty.card"
    _description = "Loyalty Card"
    _inherit = ["mail.thread"]
    _order = "issued_on desc, id desc"
    _rec_name = "card_number"

    account_id = fields.Many2one(
        "fix.loyalty.account", required=True, ondelete="cascade", index=True
    )
    card_number = fields.Char(required=True, index=True)
    barcode = fields.Char(index=True, help="What the POS scanner reads.")
    card_type = fields.Selection(
        [("physical", "Physical card"), ("wallet", "Mobile wallet"), ("virtual", "Virtual")],
        required=True,
        default="virtual",
    )
    issued_on = fields.Date(required=True, default=fields.Date.context_today)
    expires_on = fields.Date()
    state = fields.Selection(
        [("active", "Active"), ("blocked", "Blocked"), ("replaced", "Replaced")],
        required=True,
        default="active",
        tracking=True,
    )
    block_reason = fields.Char()
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )

    _number_unique = models.Constraint(
        "UNIQUE (card_number)", "A loyalty card number identifies one card."
    )

    def action_block(self, reason=""):
        if not (reason or "").strip():
            raise UserError("Blocking a card requires a stated reason.")
        for rec in self:
            rec.write({"state": "blocked", "block_reason": reason})
        return True

    @api.model
    def resolve(self, barcode_or_number):
        """The counter lookup: scan or type, get the account or nothing."""
        key = (barcode_or_number or "").strip()
        if not key:
            return self.env["fix.loyalty.account"]
        card = self.sudo().search(["|", ("card_number", "=", key), ("barcode", "=", key)], limit=1)
        if not card or card.state != "active":
            return self.env["fix.loyalty.account"]
        return card.account_id


class FixLoyaltyAccountScheme(models.Model):
    """Scheme-aware account: two balances, affiliations, requalification."""

    _inherit = "fix.loyalty.account"

    qualifying_points_balance = fields.Integer(
        string="Tier-Qualifying Points",
        readonly=True,
        copy=False,
        default=0,
        help="Points that move this member up the ladder and can NEVER be "
        "spent. Separate from points_balance so that tier marketing cannot "
        "move the IFRS-15 redemption liability.",
    )
    affiliation_member_ids = fields.One2many(
        "fix.loyalty.affiliation.member", "account_id", string="Affiliations"
    )
    card_ids = fields.One2many("fix.loyalty.card", "account_id", string="Cards")
    tier_achieved_at = fields.Date(readonly=True, help="When the current tier was reached.")
    tier_valid_until = fields.Date(
        readonly=True,
        help="When the current tier must be requalified. Empty means the "
        "programme has no retention window and the tier is held for life.",
    )
    tier_recalculated_at = fields.Datetime(readonly=True)
    last_tier_change_reason = fields.Char(readonly=True)

    def affiliation_ids_active(self):
        """The affiliations this account is currently in."""
        self.ensure_one()
        return self.affiliation_member_ids.filtered("active").mapped("affiliation_id")

    # ------------------------------------------------------------------
    # Earn / burn evaluation
    # ------------------------------------------------------------------
    def _scheme_context(
        self, amount=0.0, category=None, channel=None, product_code=None, on_date=None
    ):
        """The facts a rule is matched against. One shape, built once."""
        self.ensure_one()
        return {
            "amount": amount,
            "category": category,
            "channel": channel,
            "product_code": product_code,
            "date": on_date or fields.Date.context_today(self),
            "tier_id": self.tier_id.id or False,
            "affiliation_ids": self.affiliation_ids_active().ids,
            "account_id": self.id,
        }

    def evaluate_earn(self, amount, category=None, channel=None, product_code=None, on_date=None):
        """How many points does this transaction earn, and of what type?

        First-match-wins over the live scheme's rules in priority order, which
        is D365's documented pattern. With no live scheme the programme's
        points_per_bdt and the tier multiplier apply exactly as before —
        introducing the engine must not change the answer for a programme
        nobody has written rules for.

        Returns a dict that always explains itself, because "why did this
        customer get 40 points" is the question this engine exists to answer.
        """
        self.ensure_one()
        context = self._scheme_context(amount, category, channel, product_code, on_date)
        scheme = self.program_id.active_scheme(context["date"])
        multiplier = self.tier_id.points_multiplier or 1.0 if self.tier_id else 1.0

        if not scheme:
            points = int(amount * (self.program_id.points_per_bdt or 0.0) * multiplier)
            return {
                "points": max(0, points),
                "point_type_id": False,
                "point_class": "redeemable",
                "rule_id": False,
                "scheme_id": False,
                "basis": "No live scheme; programme rate %.4f/BDT x tier "
                "multiplier %.2f." % (self.program_id.points_per_bdt or 0.0, multiplier),
            }

        for rule in scheme.earn_rule_ids.sorted(lambda r: (r.priority, r.id)):
            if not rule.matches(context):
                continue
            if rule.excluded:
                return {
                    "points": 0,
                    "point_type_id": False,
                    "point_class": "redeemable",
                    "rule_id": rule.id,
                    "scheme_id": scheme.id,
                    "basis": "Excluded by rule '%s' — this transaction earns "
                    "nothing." % rule.name,
                }
            point_type = rule.point_type_id
            points = int(amount * rule.points_per_bdt * rule.bonus_multiplier * multiplier)
            return {
                "points": max(0, points),
                "point_type_id": point_type.id or False,
                "point_class": point_type.point_class if point_type else "redeemable",
                "rule_id": rule.id,
                "scheme_id": scheme.id,
                "basis": "Rule '%s': %.4f/BDT x bonus %.2f x tier multiplier "
                "%.2f%s."
                % (
                    rule.name,
                    rule.points_per_bdt,
                    rule.bonus_multiplier,
                    multiplier,
                    (" awarding %s points" % point_type.name) if point_type else "",
                ),
            }

        return {
            "points": 0,
            "point_type_id": False,
            "point_class": "redeemable",
            "rule_id": False,
            "scheme_id": scheme.id,
            "basis": "Scheme '%s' has no rule matching this transaction, so it "
            "earns nothing. A scheme with rules is a closed list, not a "
            "default." % scheme.code,
        }

    def evaluate_burn(self, amount, category=None, channel=None, product_code=None, on_date=None):
        """May points pay for this, and how many at most?"""
        self.ensure_one()
        context = self._scheme_context(amount, category, channel, product_code, on_date)
        scheme = self.program_id.active_scheme(context["date"])
        floor = self.program_id.min_points_to_redeem or 0

        if self.state != "active":
            return {
                "allowed": False,
                "max_points": 0,
                "max_discount_pct": 0.0,
                "rule_id": False,
                "reason": "Loyalty account is %s." % self.state,
            }
        if not scheme:
            allowed = self.points_balance >= floor
            return {
                "allowed": allowed,
                "max_points": self.points_balance if allowed else 0,
                "max_discount_pct": 100.0,
                "rule_id": False,
                "reason": "No live scheme; programme minimum of %d points " "applies." % floor,
            }

        for rule in scheme.burn_rule_ids.sorted(lambda r: (r.priority, r.id)):
            if not rule.matches(context):
                continue
            if rule.blocked:
                return {
                    "allowed": False,
                    "max_points": 0,
                    "max_discount_pct": 0.0,
                    "rule_id": rule.id,
                    "reason": "Redemption is blocked here by rule '%s'." % rule.name,
                }
            minimum = max(floor, rule.min_points)
            if self.points_balance < minimum:
                return {
                    "allowed": False,
                    "max_points": 0,
                    "max_discount_pct": 0.0,
                    "rule_id": rule.id,
                    "reason": "Rule '%s' requires %d points; balance is %d."
                    % (rule.name, minimum, self.points_balance),
                }
            ceiling = self.points_balance
            if rule.max_points_per_transaction:
                ceiling = min(ceiling, rule.max_points_per_transaction)
            return {
                "allowed": True,
                "max_points": ceiling,
                "max_discount_pct": rule.max_discount_pct,
                "rule_id": rule.id,
                "reason": "Rule '%s': up to %d points, covering at most %.0f%% "
                "of the bill." % (rule.name, ceiling, rule.max_discount_pct),
            }

        return {
            "allowed": False,
            "max_points": 0,
            "max_discount_pct": 0.0,
            "rule_id": False,
            "reason": "Scheme '%s' has no redemption rule matching this "
            "transaction." % scheme.code,
        }

    # ------------------------------------------------------------------
    # Qualifying points and tier recalculation
    # ------------------------------------------------------------------
    def award_qualifying_points(self, points, reason=""):
        """Add tier-qualifying points. These never touch points_balance."""
        if points <= 0:
            raise ValidationError("Qualifying points awarded must be positive.")
        for rec in self:
            rec.sudo().write({"qualifying_points_balance": rec.qualifying_points_balance + points})
            rec.message_post(
                body="Awarded %d tier-qualifying points (not spendable). %s" % (points, reason)
            )
            rec.recalculate_tier(trigger="qualifying_award")
        return True

    def tier_progress_points(self):
        """The number tier qualification is measured against.

        Lifetime EARNED points plus qualifying points. Deliberately not the
        spendable balance: a member who redeems should not fall down the
        ladder for having used the programme.
        """
        self.ensure_one()
        return (self.lifetime_points_earned or 0) + (self.qualifying_points_balance or 0)

    def recalculate_tier(self, trigger="manual"):
        """Re-evaluate tier UP OR DOWN, and stamp the retention window.

        Microsoft recalculates tier status after earn, return-earn or
        adjustment transactions, or on demand — so the trigger is recorded.
        The estate's check_and_update_tier() only ever promoted; this can
        also demote, which is what a retention window is for and is the half
        that was missing.
        """
        self.ensure_one()
        today = fields.Date.context_today(self)
        tiers = self.env["fix.loyalty.tier"].search(
            [("program_id", "=", self.program_id.id), ("active", "=", True)],
            order="min_points_threshold desc, min_spend_bdt desc",
        )
        progress = self.tier_progress_points()
        earned_tier = self.env["fix.loyalty.tier"]
        for tier in tiers:
            if progress >= tier.min_points_threshold or (
                self.lifetime_spend_bdt >= tier.min_spend_bdt and tier.min_spend_bdt
            ):
                earned_tier = tier
                break

        retention = self.program_id.tier_retention_months or 0
        held_tier = self.tier_id
        within_window = bool(retention and self.tier_valid_until and today <= self.tier_valid_until)

        # A tier is kept while its retention window is open, even if the
        # member no longer qualifies. That is the whole point of retention:
        # it buys the member time to requalify.
        if (
            held_tier
            and within_window
            and (not earned_tier or earned_tier.sequence > held_tier.sequence)
        ):
            self.sudo().write({"tier_recalculated_at": fields.Datetime.now()})
            return held_tier

        if earned_tier == held_tier:
            vals = {"tier_recalculated_at": fields.Datetime.now()}
            if retention and not self.tier_valid_until:
                vals["tier_valid_until"] = today + relativedelta(months=retention)
            self.sudo().write(vals)
            return held_tier

        direction = "upgraded"
        if held_tier and earned_tier and earned_tier.sequence > held_tier.sequence:
            direction = "downgraded"
        elif held_tier and not earned_tier:
            direction = "removed"

        self.sudo().write(
            {
                "tier_id": earned_tier.id or False,
                "tier_achieved_at": today,
                "tier_upgraded_date": today if direction == "upgraded" else self.tier_upgraded_date,
                "tier_valid_until": (today + relativedelta(months=retention))
                if retention
                else False,
                "tier_recalculated_at": fields.Datetime.now(),
                "last_tier_change_reason": "%s on %s (progress %d points)"
                % (direction, trigger, progress),
            }
        )
        self.message_post(
            body="Tier %s: %s -> %s (%d qualifying progress points, trigger: %s)."
            % (
                direction,
                held_tier.name if held_tier else "none",
                earned_tier.name if earned_tier else "none",
                progress,
                trigger,
            )
        )
        publish(
            self.env,
            "loyalty.tier_recalculated",
            "fix.loyalty.account",
            self.id,
            {
                "partner_id": self.partner_id.id,
                "account_no": self.name,
                "direction": direction,
                "old_tier": held_tier.code if held_tier else None,
                "new_tier": earned_tier.code if earned_tier else None,
                "progress_points": progress,
                "trigger": trigger,
                "valid_until": str(self.tier_valid_until) if self.tier_valid_until else None,
            },
        )
        return earned_tier

    @api.model
    def cron_requalify_tiers(self):
        """Recalculate tiers whose retention window has closed.

        Without this the window is decorative: a member keeps a tier they
        stopped qualifying for because nothing ever looks again.
        """
        today = fields.Date.context_today(self)
        due = self.sudo().search(
            [
                ("state", "=", "active"),
                ("tier_valid_until", "!=", False),
                ("tier_valid_until", "<", today),
            ]
        )
        for account in due:
            account.recalculate_tier(trigger="retention_window_expired")
        return len(due)
