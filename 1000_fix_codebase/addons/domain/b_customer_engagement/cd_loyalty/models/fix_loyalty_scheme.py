# M10 — the loyalty SCHEME engine: earn rules, burn rules, affiliations,
# point types and tier requalification.
#
# WHAT WAS HERE BEFORE. One float, `points_per_bdt`, multiplied by a tier
# multiplier, with a campaign hook that could add a bonus. That expresses
# exactly one rule: everybody earns the same rate on everything. It cannot
# express "double points on parts in Ramadan", "corporate AMC staff earn at
# the dealer rate", or "Gold earns on parts and Silver does not" — and the
# last one is not an exotic request, it is how tiers are normally sold.
#
# FOUR THINGS THE NOVEMBER 2026 RESEARCH CHANGED, each of which is a schema
# decision rather than a feature, which is why the gap plan pulled them in
# ahead of the engine being written:
#
#   1. RULES DIFFER BY TIER. Microsoft: "retailers can create different
#      earning and redemption rules by tiers". The estate expressed tier
#      benefit only as a multiplier, which cannot say "Silver does not earn
#      on this category at all". So fix.loyalty.earn.rule carries an OPTIONAL
#      tier_id. Adding it after the engine shipped would have meant
#      rewriting the engine.
#
#   2. AFFILIATIONS vary rewards for a cohort WITHOUT creating a tier. The
#      first pass missed the concept entirely. It matters here directly:
#      corporate AMC staff, dealer technicians and campaign cohorts all need
#      distinct earn rates while staying in the ordinary consumer ladder.
#      Without it every such request becomes a new tier and the ladder
#      degrades into a list of special cases.
#
#   3. NON-REDEEMABLE (TIER-QUALIFYING) POINTS. D365 separates points that
#      BUY things from points that only MOVE YOU UP. The estate had a single
#      integer balance, so every point was spendable — which meant tier
#      progression and redemption liability were the same number, and a
#      campaign that accelerated tier progress unavoidably inflated the
#      IFRS-15 liability. Two point classes decouple them. This is a
#      prerequisite for point types, not an alternative to them.
#
#   4. TIER RETENTION is a duration, and tier status is RECALCULATED after
#      earn, return-earn or adjustment transactions, or on demand. The
#      estate had a lifetime threshold and no recalculation trigger, so a
#      tier could only ever go up.
#
# Rules are evaluated in priority order, first match wins, which is D365's
# documented pattern and the only one that makes a rule set debuggable.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

# What a rule can key on. A whitelist for the same reason the journey branch
# has one: these are authored by marketing, not by engineering.
EARN_DIMENSIONS = [
    ("all", "All transactions"),
    ("category", "Service category"),
    ("channel", "Sales channel"),
    ("product", "Specific product"),
    ("min_amount", "Transaction at or above an amount"),
]

POINT_CLASSES = [
    ("redeemable", "Redeemable — spendable, and an IFRS-15 liability"),
    ("qualifying", "Tier-qualifying only — counts toward tier, never spendable"),
]


class FixLoyaltyPointType(models.Model):
    """A point currency. Separates what points DO from what they are worth.

    The gap plan lists point types and non-redeemable points as two rows. They
    are one mechanism: a point type whose class is 'qualifying' is a
    non-redeemable point, and one whose class is 'redeemable' is an ordinary
    one. Modelling them separately would have produced two overlapping ideas.
    """

    _name = "fix.loyalty.point.type"
    _description = "Loyalty Point Type"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    name_bn = fields.Char(string="Name (Bengali)", help="DE-17")
    code = fields.Char(required=True, index=True)
    program_id = fields.Many2one(
        "fix.loyalty.program", required=True, ondelete="cascade", index=True
    )
    point_class = fields.Selection(
        POINT_CLASSES,
        required=True,
        default="redeemable",
        help="A qualifying point moves a member up the ladder and can never "
        "be spent, so it carries no redemption liability. This is what "
        "decouples tier marketing from the IFRS-15 number.",
    )
    bdt_per_point = fields.Float(
        default=1.0,
        help="Redemption value. Meaningless, and forced to 0, for a " "qualifying point type.",
    )
    expiry_months = fields.Integer(default=12, help="0 means these points do not expire.")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )

    _code_unique = models.Constraint(
        "UNIQUE (program_id, code)", "Each point type code exists once per programme."
    )

    @api.constrains("point_class", "bdt_per_point")
    def _check_qualifying_has_no_value(self):
        for rec in self:
            if rec.point_class == "qualifying" and rec.bdt_per_point:
                raise ValidationError(
                    "Point type '%s' is tier-qualifying only, so it cannot "
                    "carry a redemption value. A qualifying point with a BDT "
                    "value is a redeemable point with a misleading label — and "
                    "it would reappear in the IFRS-15 liability, which is the "
                    "exact coupling this class exists to break." % rec.name
                )


class FixLoyaltyAffiliation(models.Model):
    """A cohort whose reward rates differ, without a tier of its own.

    Microsoft's affiliations. For 1000FiX the obvious members are corporate
    AMC staff, dealer technicians and campaign cohorts: all of them need a
    different earn rate while staying in the ordinary consumer ladder.
    """

    _name = "fix.loyalty.affiliation"
    _description = "Loyalty Affiliation"
    _order = "name"

    name = fields.Char(required=True)
    name_bn = fields.Char(string="Name (Bengali)", help="DE-17")
    code = fields.Char(required=True, index=True)
    program_id = fields.Many2one(
        "fix.loyalty.program", required=True, ondelete="cascade", index=True
    )
    description = fields.Text()
    member_ids = fields.One2many(
        "fix.loyalty.affiliation.member", "affiliation_id", string="Members"
    )
    member_count = fields.Integer(compute="_compute_member_count")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )

    _code_unique = models.Constraint(
        "UNIQUE (program_id, code)", "Each affiliation code exists once per programme."
    )

    @api.depends("member_ids.active")
    def _compute_member_count(self):
        for rec in self:
            rec.member_count = len(rec.member_ids.filtered("active"))

    def add_members(self, accounts, reason=""):
        """Enrol loyalty accounts into this cohort."""
        self.ensure_one()
        Member = self.env["fix.loyalty.affiliation.member"]
        added = Member.browse()
        for account in accounts:
            existing = Member.search(
                [("affiliation_id", "=", self.id), ("account_id", "=", account.id)],
                limit=1,
            )
            if existing:
                if not existing.active:
                    existing.write({"active": True, "reason": reason})
                continue
            added |= Member.create(
                {
                    "affiliation_id": self.id,
                    "account_id": account.id,
                    "reason": reason,
                }
            )
        return added


class FixLoyaltyAffiliationMember(models.Model):
    """One account's membership of one affiliation."""

    _name = "fix.loyalty.affiliation.member"
    _description = "Loyalty Affiliation Member"
    _order = "affiliation_id, account_id"
    _rec_name = "account_id"

    affiliation_id = fields.Many2one(
        "fix.loyalty.affiliation", required=True, ondelete="cascade", index=True
    )
    account_id = fields.Many2one(
        "fix.loyalty.account", required=True, ondelete="cascade", index=True
    )
    joined_at = fields.Datetime(required=True, default=fields.Datetime.now)
    reason = fields.Char(
        help="Why this member qualifies. Affiliations are a "
        "commercial decision and should say whose."
    )
    active = fields.Boolean(default=True)

    _member_unique = models.Constraint(
        "UNIQUE (affiliation_id, account_id)",
        "An account belongs to each affiliation once.",
    )


class FixLoyaltyScheme(models.Model):
    """A named set of earn and burn rules. The D365 loyalty scheme."""

    _name = "fix.loyalty.scheme"
    _description = "Loyalty Scheme"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.dofa.mixin"]

    # A03 audit R7: the scheme's cost is approved from the M63 inbox.
    _approval_domain = "loyalty_scheme"
    _approval_routed = True
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True, tracking=True)
    name_bn = fields.Char(string="Name (Bengali)", help="DE-17")
    code = fields.Char(required=True, index=True)
    program_id = fields.Many2one(
        "fix.loyalty.program", required=True, ondelete="cascade", index=True
    )
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("retired", "Retired")],
        required=True,
        default="draft",
        tracking=True,
    )
    valid_from = fields.Date()
    valid_until = fields.Date()
    earn_rule_ids = fields.One2many("fix.loyalty.earn.rule", "scheme_id", string="Earn Rules")
    burn_rule_ids = fields.One2many("fix.loyalty.burn.rule", "scheme_id", string="Redemption Rules")
    # Scheme activation is a commercial commitment: it changes what every
    # future transaction costs the business. The gap plan puts it at
    # marketing Tier 3.
    estimated_annual_cost = fields.Monetary(
        string="Estimated Annual Cost (BDT)",
        currency_field="currency_id",
        help="The cost this scheme is expected to add. Drives the DOFA tier; "
        "it is an input to a decision, never a measured figure.",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", index=True)

    _code_unique = models.Constraint("UNIQUE (code)", "Each scheme code exists once.")

    # --- DOFA ---
    def _dofa_amount(self) -> float:
        self.ensure_one()
        return self.estimated_annual_cost or 0.0

    def _dofa_thresholds(self):
        """The SAME ladder as the campaign budget it competes for money with.

        M35: nothing below BDT 50,000, Tier 3 above it, Tier 4 above
        BDT 200,000. An earlier draft of this method started at Tier 2, which
        would have sent a one-taka scheme to a supervisor -- and it claimed
        in its own docstring to match M35 while not matching it.
        """
        return [(50000.0, "tier_0"), (200000.0, "tier_3"), (10000000.0, "tier_4")]

    @api.depends("estimated_annual_cost")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def _fix_guarded_fields(self) -> set:
        # Writing state='active' put a Tier-4 scheme live with no approval.
        return super()._fix_guarded_fields() | {"state"}

    def action_activate(self):
        for rec in self:
            if rec.state == "active":
                raise UserError("This scheme is already active.")
            if not rec.earn_rule_ids and not rec.burn_rule_ids:
                raise UserError(
                    "A scheme with no rules changes nothing. Add an earn or a "
                    "redemption rule before activating."
                )
            rec._dofa_assert_approved(what="Activating loyalty scheme '%s'" % rec.name)
            rec._guarded().write({"state": "active"})
            publish(
                self.env,
                "loyalty.scheme_activated",
                "fix.loyalty.scheme",
                rec.id,
                {
                    "scheme": rec.code,
                    "programme": rec.program_id.code,
                    "earn_rules": len(rec.earn_rule_ids),
                    "burn_rules": len(rec.burn_rule_ids),
                    "estimated_annual_cost": rec.estimated_annual_cost,
                },
            )
        return True

    def action_retire(self):
        for rec in self:
            rec._guarded().write({"state": "retired"})
            # Re-activation is a new commitment. The old sign-off covered the
            # scheme as it stood then, not whatever it is edited into later.
            rec._dofa_void_approval("scheme retired; re-activation needs a fresh approval")
        return True

    def is_live(self, on_date=None):
        self.ensure_one()
        day = on_date or fields.Date.context_today(self)
        if self.state != "active" or not self.active:
            return False
        if self.valid_from and day < self.valid_from:
            return False
        return not (self.valid_until and day > self.valid_until)


class FixLoyaltyEarnRule(models.Model):
    """One earn rule. May be scoped to a tier, an affiliation, or both."""

    _name = "fix.loyalty.earn.rule"
    _description = "Loyalty Earn Rule"
    _order = "scheme_id, priority, id"

    scheme_id = fields.Many2one("fix.loyalty.scheme", required=True, ondelete="cascade", index=True)
    name = fields.Char(required=True)
    priority = fields.Integer(
        required=True,
        default=10,
        help="Lower runs first. Rules are first-match-wins, as D365 does it.",
    )
    dimension = fields.Selection(EARN_DIMENSIONS, required=True, default="all")
    dimension_value = fields.Char(
        help="The category, channel or product code the dimension matches. "
        "For 'min_amount', the threshold in BDT."
    )
    # --- the tier scoping the first pass missed ---
    tier_id = fields.Many2one(
        "fix.loyalty.tier",
        string="Applies To Tier",
        help="Empty means every tier. This field is the whole reason the "
        "scheme engine could not be written first: 'Gold earns on parts and "
        "Silver does not' is inexpressible without it, and retrofitting it "
        "would mean rebuilding the evaluator.",
    )
    affiliation_id = fields.Many2one(
        "fix.loyalty.affiliation",
        string="Applies To Affiliation",
        help="Empty means every member. Lets a cohort earn differently "
        "without inflating the tier ladder.",
    )
    point_type_id = fields.Many2one(
        "fix.loyalty.point.type",
        string="Awards Point Type",
        help="Empty awards the programme's ordinary redeemable points.",
    )
    points_per_bdt = fields.Float(
        required=True,
        default=0.01,
        help="Points per BDT for transactions this rule matches.",
    )
    bonus_multiplier = fields.Float(
        required=True,
        default=1.0,
        help="Applied on top of the rate. A bonus period is a rule with a "
        "multiplier and a validity window, not a special case in code.",
    )
    excluded = fields.Boolean(
        string="Earns Nothing",
        default=False,
        help="A matching transaction earns ZERO and rule evaluation stops. "
        "This is how an exclusion is expressed — as a rule, so that it is "
        "visible and ordered like every other rule.",
    )
    valid_from = fields.Date()
    valid_until = fields.Date()
    active = fields.Boolean(default=True)

    @api.constrains("points_per_bdt", "bonus_multiplier")
    def _check_rates(self):
        for rec in self:
            if rec.points_per_bdt < 0:
                raise ValidationError("An earn rate cannot be negative.")
            if rec.bonus_multiplier < 0:
                raise ValidationError("A bonus multiplier cannot be negative.")

    def matches(self, context):
        """Does this rule apply to the transaction described by `context`?"""
        self.ensure_one()
        if not self.active:
            return False
        day = context.get("date") or fields.Date.context_today(self)
        if self.valid_from and day < self.valid_from:
            return False
        if self.valid_until and day > self.valid_until:
            return False
        if self.tier_id and context.get("tier_id") != self.tier_id.id:
            return False
        if self.affiliation_id and self.affiliation_id.id not in (
            context.get("affiliation_ids") or []
        ):
            return False
        value = (self.dimension_value or "").strip().lower()
        if self.dimension == "all":
            return True
        if self.dimension == "category":
            return (context.get("category") or "").strip().lower() == value
        if self.dimension == "channel":
            return (context.get("channel") or "").strip().lower() == value
        if self.dimension == "product":
            return (context.get("product_code") or "").strip().lower() == value
        if self.dimension == "min_amount":
            try:
                return float(context.get("amount") or 0.0) >= float(value or 0)
            except ValueError:
                return False
        return False


class FixLoyaltyBurnRule(models.Model):
    """One redemption rule. Also tier- and affiliation-scopable."""

    _name = "fix.loyalty.burn.rule"
    _description = "Loyalty Redemption Rule"
    _order = "scheme_id, priority, id"

    scheme_id = fields.Many2one("fix.loyalty.scheme", required=True, ondelete="cascade", index=True)
    name = fields.Char(required=True)
    priority = fields.Integer(required=True, default=10)
    dimension = fields.Selection(EARN_DIMENSIONS, required=True, default="all")
    dimension_value = fields.Char()
    tier_id = fields.Many2one("fix.loyalty.tier", string="Applies To Tier")
    affiliation_id = fields.Many2one("fix.loyalty.affiliation", string="Applies To Affiliation")
    min_points = fields.Integer(
        default=0, help="Minimum balance before this rule allows a redemption."
    )
    max_points_per_transaction = fields.Integer(
        default=0, help="0 means no per-transaction ceiling."
    )
    max_discount_pct = fields.Float(
        default=100.0,
        help="Ceiling on how much of a bill points may cover under this rule.",
    )
    blocked = fields.Boolean(
        string="Redemption Blocked",
        default=False,
        help="A matching transaction may not be paid with points at all.",
    )
    valid_from = fields.Date()
    valid_until = fields.Date()
    active = fields.Boolean(default=True)

    @api.constrains("max_discount_pct")
    def _check_pct(self):
        for rec in self:
            if not (0 <= rec.max_discount_pct <= 100):
                raise ValidationError("A discount ceiling must be between 0 and 100 percent.")

    def matches(self, context):
        self.ensure_one()
        if not self.active:
            return False
        day = context.get("date") or fields.Date.context_today(self)
        if self.valid_from and day < self.valid_from:
            return False
        if self.valid_until and day > self.valid_until:
            return False
        if self.tier_id and context.get("tier_id") != self.tier_id.id:
            return False
        if self.affiliation_id and self.affiliation_id.id not in (
            context.get("affiliation_ids") or []
        ):
            return False
        value = (self.dimension_value or "").strip().lower()
        if self.dimension == "all":
            return True
        if self.dimension == "category":
            return (context.get("category") or "").strip().lower() == value
        if self.dimension == "channel":
            return (context.get("channel") or "").strip().lower() == value
        if self.dimension == "product":
            return (context.get("product_code") or "").strip().lower() == value
        if self.dimension == "min_amount":
            try:
                return float(context.get("amount") or 0.0) >= float(value or 0)
            except ValueError:
                return False
        return False
