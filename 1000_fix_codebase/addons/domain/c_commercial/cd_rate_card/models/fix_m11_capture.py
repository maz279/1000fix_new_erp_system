# M11 capture audit, pass 2 (18 Nov 2026).
#
# The 13 Nov pass gave every M11 sub-module page a "+ New". Read against the
# spec, four pages still could not record what they exist for:
#
#   page 4 Parts Pricing  - FR-PRC-013 (P0): parts are priced by markup on
#       cost, banded markup by cost tier or a provenance-grade differential.
#       A part could only get a fixed rate card; the ~18,000-row parts list
#       (spec §16.4) had nowhere to go. -> fix.parts.price.scheme (+ bands)
#   page 9 Adjustment Rules - FR-PRC-018/019 (P1): urgency, after-hours,
#       weekend, holiday, zone and distance premiums (spec entity
#       fix.price.adjustment). Only the W7 marketplace/storefront dynamic
#       rule existed. -> fix.price.adjustment
#   page 11 Versioning & Approval - FR-PRC-024 / BRU-PRC-16 (H): a mass price
#       change across a filtered set with preview, approval, a scheduled
#       effective date and one-step rollback; immediate = CCO approval.
#       Only one change request per rate existed. -> fix.price.mass.change
#   page 5 Contract Pricing - FR-PRC-016 / AC-08: a contract rate named its
#       contract by typed text, so a typo priced a contract that does not
#       exist and the rate never lapsed with the contract.
#       -> fix.rate.card.contract_id (M08)
#
# Every new record follows the module's release control: a Pricing Officer
# records it, a Price-Book Releaser who did not author it releases it from
# the M63 inbox (BRU-PRC-07), and released terms never change.
import itertools
import json
from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

from .pricing_roles import ROLE_OFFICER, ROLE_RELEASER, require_releaser_not_author, require_role

GROUP_CCO = "cd_entity_config.group_dofa_tier_4"

PROVENANCE_GRADES = [
    ("genuine", "Genuine (brand-supplied)"),
    ("oem", "OEM (original manufacturer, unbranded)"),
    ("aftermarket", "Aftermarket / compatible"),
    ("refurbished", "Refurbished / reclaimed"),
]
LINE_TYPES = [
    ("labour", "Labour"),
    ("part", "Part"),
    ("consumable", "Consumable"),
    ("transport", "Transport"),
]
RELEASE_STATES = [
    ("draft", "Draft"),
    ("in_review", "In Review"),
    ("active", "In Force"),
    ("superseded", "Superseded"),
    ("retired", "Retired"),
]


def _money(value, step=0.01):
    """Round half-up to `step` (0.01 = the paisa; 1, 5, 10 = whole-taka
    rounding per FR-PRC-008), in Decimal."""
    step = Decimal(str(step or 0.01))
    units = (Decimal(str(value)) / step).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return float(units * step)


class FixApprovalMatrixM11Capture(models.Model):
    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[
            ("pricing_parts_scheme", "Parts Pricing Scheme Release"),
            ("pricing_adjustment", "Price Premium / Surcharge Release"),
            ("pricing_mass_change", "Mass Price Change"),
        ],
        ondelete=dict.fromkeys(
            ("pricing_parts_scheme", "pricing_adjustment", "pricing_mass_change"), "cascade"
        ),
    )


class _M11Released(models.AbstractModel):
    """Shared release lifecycle: Draft -> In Review -> In Force (-> Superseded
    or Retired). Terms named in `_release_terms` freeze once the record leaves
    Draft; the releaser is a Price-Book Releaser who is not the author."""

    _name = "fix.m11.released.mixin"
    _description = "M11 released pricing record"
    _inherit = ["mail.thread", "fix.approvable.mixin"]

    _approval_apply_method = "action_approve"
    _approval_group = ROLE_RELEASER
    _approval_routed = True
    _release_terms = frozenset()
    _release_what = "pricing record"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    valid_from = fields.Date(string="Effective From", required=True)
    valid_to = fields.Date(string="Effective Until", copy=False)
    state = fields.Selection(
        RELEASE_STATES, required=True, default="draft", readonly=True, tracking=True
    )
    version = fields.Integer(readonly=True, copy=False)
    submitted_by = fields.Many2one("res.users", readonly=True, copy=False)
    approved_by = fields.Many2one("res.users", string="Released By", readonly=True, copy=False)
    approved_at = fields.Datetime(string="Released On", readonly=True, copy=False)
    retired_reason = fields.Char(readonly=True, copy=False)
    note = fields.Text()

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "version",
            "submitted_by",
            "approved_by",
            "approved_at",
            "retired_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(rec.state != "draft" for rec in self):
            locked |= set(self._release_terms) | {"valid_to"}
        return locked

    def _approval_pinned_fields(self) -> set:
        return super()._approval_pinned_fields() | set(self._release_terms)

    @api.constrains("valid_from", "valid_to")
    def _check_window(self):
        for rec in self:
            if rec.valid_from and rec.valid_to and rec.valid_to < rec.valid_from:
                raise ValidationError("%s ends before it starts." % rec.display_name)

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, (ROLE_OFFICER,), "Recording a %s" % self._release_what)
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open():
            require_role(self.env, (ROLE_OFFICER,), "Changing a %s" % self._release_what)
            touched = (set(self._release_terms) | {"valid_to"}) & set(vals)
            for rec in self:
                if rec.state == "draft" or not touched:
                    continue
                moved = [n for n in touched if rec._fix_guard_differs(n, vals[n], rec[n])]
                if moved:
                    raise UserError(
                        "%s is %s: %s cannot change any more; its release covered them. "
                        "Record a new one with its own effective date."
                        % (
                            rec.display_name,
                            dict(RELEASE_STATES)[rec.state],
                            ", ".join(sorted(rec._fields[n].string or n for n in moved)),
                        )
                    )
        return super().write(vals)

    # ---- lifecycle -----------------------------------------------------------
    def _scope_domain(self):
        """Records competing for the same scope (superseded on release)."""
        self.ensure_one()
        return [("company_id", "=", self.company_id.id)]

    def _release_check(self):
        """Raise when this record cannot be released as it stands."""
        self.ensure_one()

    def action_request_approval(self, justification=None):
        require_role(self.env, (ROLE_OFFICER,), "Submitting a %s" % self._release_what)
        for rec in self:
            resubmit = rec.state == "in_review" and rec.approval_state in ("none", "returned")
            if rec.state != "draft" and not resubmit:
                raise UserError("Only a Draft %s is submitted for release." % self._release_what)
            rec._release_check()
            later = self.search(
                [
                    *rec._scope_domain(),
                    ("id", "!=", rec.id),
                    ("state", "in", ("active", "superseded", "retired")),
                    ("valid_from", ">=", rec.valid_from),
                ],
                limit=1,
            )
            if later:
                raise UserError(
                    "%s already prices this scope from %s; a new version starts after it."
                    % (later.display_name, later.valid_from)
                )
            rec._guarded().write({"state": "in_review", "submitted_by": self.env.uid})
        return super().action_request_approval(justification=justification)

    def action_submit(self):
        return self.action_request_approval()

    def action_approve(self):
        """Release from the releaser's M63 inbox: in force from its effective
        date; the version it follows keeps its window to the day before."""
        self._approval_assert_routed()
        authority = self._approval_authority_user()
        acting = self._approval_acting_users()
        for rec in self:
            if rec.state != "in_review":
                raise UserError("Only a %s In Review is released." % self._release_what)
            require_releaser_not_author(
                self.env,
                authority,
                acting,
                rec,
                rec.create_uid | rec.submitted_by,
                "Releasing a %s" % self._release_what,
            )
            rec._release_check()
            siblings = self.search(
                [
                    *rec._scope_domain(),
                    ("id", "!=", rec.id),
                    ("state", "in", ("active", "superseded", "retired")),
                ]
            )
            previous = siblings.filtered(lambda r: r.state == "active")
            if previous:
                previous._guarded().write(
                    {"state": "superseded", "valid_to": rec.valid_from - timedelta(days=1)}
                )
            rec._guarded().write(
                {
                    "state": "active",
                    "version": max(siblings.mapped("version") or [0]) + 1,
                    "approved_by": self.env.uid,
                    "approved_at": fields.Datetime.now(),
                }
            )
            rec.message_post(body="Released by %s." % self.env.user.name)
        return True

    def _approval_on_rejected(self, comment):
        self.filtered(lambda r: r.state == "in_review")._guarded().write({"state": "draft"})
        return super()._approval_on_rejected(comment)

    def action_recall_approval(self):
        result = super().action_recall_approval()
        self.filtered(lambda r: r.state == "in_review")._guarded().write({"state": "draft"})
        return result

    def action_retire(self, reason=None):
        require_role(
            self.env,
            (ROLE_RELEASER,),
            "Retiring a %s" % self._release_what,
            role="Price-Book Releaser",
        )
        if not (reason or "").strip():
            raise UserError("State why it is retired.")
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state != "active":
                raise UserError("Only a %s in force is retired." % self._release_what)
            rec._guarded().write(
                {
                    "state": "retired",
                    "valid_to": max(today, rec.valid_from),
                    "retired_reason": reason.strip(),
                }
            )
            rec.message_post(body="Retired: %s" % reason.strip())
        return True

    def _in_force_on(self, day):
        self.ensure_one()
        return bool(
            self.state in ("active", "superseded", "retired")
            and self.valid_from <= day
            and (not self.valid_to or self.valid_to >= day)
        )


# =========================================================================
# Page 4 - Parts Pricing (FR-PRC-013)
# =========================================================================
SCHEME_METHODS = [
    ("markup", "Markup on cost"),
    ("banded", "Banded markup by cost tier"),
    ("grade", "Markup with a provenance-grade differential"),
    ("fixed", "Fixed price"),
]


class FixPartsPriceScheme(models.Model):
    """How a spare part's selling price follows from its cost."""

    _name = "fix.parts.price.scheme"
    _description = "Parts Pricing Scheme"
    _inherit = ["fix.m11.released.mixin"]
    _order = "category_id, brand_id, provenance_grade, valid_from desc, id desc"

    _approval_domain = "pricing_parts_scheme"
    _release_what = "parts pricing scheme"
    _release_terms = frozenset(
        {
            "category_id",
            "brand_id",
            "provenance_grade",
            "method",
            "markup_pct",
            "fixed_price",
            "genuine_adj_pct",
            "oem_adj_pct",
            "aftermarket_adj_pct",
            "refurbished_adj_pct",
            "rounding_step",
            "currency_id",
            "valid_from",
            "company_id",
        }
    )

    # declared in the class body too: the isolation generator reads it here
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    name = fields.Char(required=True)
    category_id = fields.Many2one(
        "product.category",
        string="Part Category",
        help="Empty = every part category.",
    )
    brand_id = fields.Many2one("fix.brand", string="Brand", help="Empty = every brand.")
    provenance_grade = fields.Selection(
        PROVENANCE_GRADES,
        string="Provenance Grade",
        help="Empty = every grade. A scheme for one grade wins over an all-grade one.",
    )
    method = fields.Selection(SCHEME_METHODS, required=True, default="markup")
    markup_pct = fields.Float(
        string="Markup on Cost (%)",
        help="Markup and grade methods: selling price = cost x (1 + markup).",
    )
    fixed_price = fields.Monetary(
        string="Fixed Price", currency_field="currency_id", help="Fixed-price method only."
    )
    band_ids = fields.One2many("fix.parts.price.band", "scheme_id", string="Cost Bands", copy=True)
    genuine_adj_pct = fields.Float(string="Genuine: Markup Adjustment (pts)")
    oem_adj_pct = fields.Float(string="OEM: Markup Adjustment (pts)")
    aftermarket_adj_pct = fields.Float(string="Aftermarket: Markup Adjustment (pts)")
    refurbished_adj_pct = fields.Float(string="Refurbished: Markup Adjustment (pts)")
    rounding_step = fields.Float(
        string="Round Selling Price To (BDT)",
        default=1.0,
        help="0.01 = to the paisa; 1, 5 or 10 = whole taka (FR-PRC-008).",
    )

    def _scope_domain(self):
        self.ensure_one()
        return [
            ("company_id", "=", self.company_id.id),
            ("category_id", "=", self.category_id.id or False),
            ("brand_id", "=", self.brand_id.id or False),
            ("provenance_grade", "=", self.provenance_grade or False),
        ]

    @api.constrains("method", "markup_pct", "fixed_price", "rounding_step")
    def _check_terms(self):
        for rec in self:
            if rec.method in ("markup", "grade") and not 0.0 <= rec.markup_pct <= 1000.0:
                raise ValidationError("A markup on cost runs from 0 to 1000%.")
            if rec.method == "fixed" and rec.fixed_price <= 0:
                raise ValidationError("A fixed-price scheme needs a positive price.")
            if rec.rounding_step < 0:
                raise ValidationError("The rounding step cannot be negative.")

    def _release_check(self):
        self.ensure_one()
        if self.method == "banded":
            self.band_ids._check_ladder(self)

    def _grade_adjustment(self, grade):
        self.ensure_one()
        return {
            "genuine": self.genuine_adj_pct,
            "oem": self.oem_adj_pct,
            "aftermarket": self.aftermarket_adj_pct,
            "refurbished": self.refurbished_adj_pct,
        }.get(grade or "", 0.0)

    def price_for(self, cost, grade=None):
        """The selling price of a part costing `cost` under this scheme."""
        self.ensure_one()
        if self.method == "fixed":
            return _money(self.fixed_price, self.rounding_step)
        cost = float(cost or 0.0)
        if cost <= 0:
            raise UserError("A part priced on cost needs a positive cost.")
        if self.method == "banded":
            markup = self.band_ids._markup_for(cost)
            if markup is None:
                raise UserError("No cost band of %s covers a cost of %.2f." % (self.name, cost))
        else:
            markup = self.markup_pct
            if self.method == "grade":
                markup += self._grade_adjustment(grade)
        if markup < 0:
            raise UserError("The %s grade would sell this part below its cost." % (grade or ""))
        return _money(cost * (1.0 + markup / 100.0), self.rounding_step)

    @api.model
    def scheme_for(self, category=None, brand=None, grade=None, on_date=None, company=None):
        """The released scheme that prices a part: the most specific scope
        (grade, brand, category) wins; versions by their window."""
        day = on_date or fields.Date.context_today(self)
        company = company or self.env.company
        found = self.sudo().search(
            [
                ("company_id", "=", company.id),
                ("state", "in", ("active", "superseded", "retired")),
                ("valid_from", "<=", day),
                "|",
                ("valid_to", "=", False),
                ("valid_to", ">=", day),
                ("category_id", "in", [False, category.id if category else False]),
                ("brand_id", "in", [False, brand.id if brand else False]),
                ("provenance_grade", "in", [False, grade or False]),
            ]
        )

        def rank(s):
            return (
                bool(s.provenance_grade),
                bool(s.brand_id),
                bool(s.category_id),
                s.valid_from,
                s.id,
            )

        return max(found, key=rank) if found else self.browse()


class FixPartsPriceBand(models.Model):
    _name = "fix.parts.price.band"
    _description = "Parts Pricing Cost Band"
    _order = "scheme_id, cost_from"

    scheme_id = fields.Many2one(
        "fix.parts.price.scheme", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="scheme_id.company_id", store=True)
    cost_from = fields.Float(string="Cost From (BDT)", required=True, default=0.0)
    cost_to = fields.Float(string="Cost Up To (BDT)", help="0 = no upper limit (last band).")
    markup_pct = fields.Float(string="Markup (%)", required=True)

    def _assert_draft(self, schemes):
        if schemes.filtered(lambda s: s.state != "draft"):
            raise UserError(
                "The cost bands of a released parts scheme cannot change; record a new "
                "version of the scheme."
            )

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, (ROLE_OFFICER,), "Recording a parts cost band")
        records = super().create(vals_list)
        self._assert_draft(records.mapped("scheme_id"))
        return records

    def write(self, vals):
        require_role(self.env, (ROLE_OFFICER,), "Changing a parts cost band")
        self._assert_draft(self.mapped("scheme_id"))
        return super().write(vals)

    def unlink(self):
        require_role(self.env, (ROLE_OFFICER,), "Removing a parts cost band")
        self._assert_draft(self.mapped("scheme_id"))
        return super().unlink()

    @api.constrains("cost_from", "cost_to", "markup_pct")
    def _check_band(self):
        for band in self:
            if band.cost_from < 0 or (band.cost_to and band.cost_to <= band.cost_from):
                raise ValidationError("A cost band ends after it starts.")
            if not 0.0 <= band.markup_pct <= 1000.0:
                raise ValidationError("A band markup runs from 0 to 1000%.")

    def _check_ladder(self, scheme):
        bands = scheme.band_ids.sorted("cost_from")
        if not bands:
            raise UserError("A banded scheme needs its cost bands.")
        if bands[0].cost_from > 0:
            raise UserError("The first cost band starts at 0.")
        for low, high in itertools.pairwise(bands):
            if not low.cost_to or abs(low.cost_to - high.cost_from) > 0.005:
                raise UserError(
                    "Cost bands must meet without a gap or an overlap (%.2f then %.2f)."
                    % (low.cost_to, high.cost_from)
                )

    def _markup_for(self, cost):
        for band in self.sorted("cost_from"):
            if cost >= band.cost_from and (not band.cost_to or cost < band.cost_to):
                return band.markup_pct
        return None


# =========================================================================
# Page 9 - Adjustment Rules (FR-PRC-018 zone/distance, FR-PRC-019 urgency)
# =========================================================================
ADJUSTMENT_TYPES = [
    ("express", "Express service"),
    ("emergency", "Emergency call-out"),
    ("after_hours", "After-hours"),
    ("weekend", "Weekend"),
    ("holiday", "Public holiday"),
    ("zone", "Branch zone"),
    ("distance", "Distance band"),
]


class FixPriceAdjustment(models.Model):
    """A declared premium or surcharge on the base rate. It is applied as a
    named line of the price explanation, never folded silently into it."""

    _name = "fix.price.adjustment"
    _description = "Price Premium / Surcharge"
    _inherit = ["fix.m11.released.mixin"]
    _order = "adjustment_type, code, valid_from desc"

    _approval_domain = "pricing_adjustment"
    _release_what = "price premium"
    _release_terms = frozenset(
        {
            "code",
            "adjustment_type",
            "basis",
            "value",
            "applies_to",
            "operating_unit_ids",
            "distance_from_km",
            "distance_to_km",
            "hour_from",
            "hour_to",
            "currency_id",
            "valid_from",
            "company_id",
        }
    )

    # declared in the class body too: the isolation generator reads it here
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    adjustment_type = fields.Selection(ADJUSTMENT_TYPES, required=True, default="express")
    basis = fields.Selection(
        [("percent", "% of the base rate"), ("fixed", "Fixed amount")],
        required=True,
        default="percent",
    )
    value = fields.Float(required=True)
    applies_to = fields.Selection(
        [("all", "Every line"), *LINE_TYPES],
        string="Applies To",
        required=True,
        default="labour",
    )
    operating_unit_ids = fields.Many2many(
        "operating.unit",
        "fix_price_adjustment_ou_rel",
        "adjustment_id",
        "operating_unit_id",
        string="Branches in the Zone",
        help="Zone premiums: the branches the premium applies at.",
    )
    distance_from_km = fields.Float(string="Distance From (km)")
    distance_to_km = fields.Float(string="Distance Up To (km)", help="0 = no upper limit.")
    hour_from = fields.Float(string="From Hour", help="After-hours premiums: 24-hour clock.")
    hour_to = fields.Float(string="To Hour")

    def _scope_domain(self):
        self.ensure_one()
        return [("company_id", "=", self.company_id.id), ("code", "=", self.code)]

    @api.constrains(
        "basis", "value", "adjustment_type", "distance_from_km", "distance_to_km", "hour_from"
    )
    def _check_terms(self):
        for rec in self:
            if rec.value <= 0:
                raise ValidationError("A premium is a positive amount; a discount is not one.")
            if rec.basis == "percent" and rec.value > 100.0:
                raise ValidationError("A percentage premium is at most 100% of the base rate.")
            if rec.adjustment_type == "distance" and (
                rec.distance_from_km < 0
                or (rec.distance_to_km and rec.distance_to_km <= rec.distance_from_km)
            ):
                raise ValidationError("A distance band ends after it starts.")
            if rec.adjustment_type == "after_hours":
                for hour in (rec.hour_from, rec.hour_to):
                    if not 0.0 <= hour <= 24.0:
                        raise ValidationError("Hours run from 0 to 24.")
                if rec.hour_from == rec.hour_to:
                    raise ValidationError("An after-hours window needs a start and an end.")

    def _release_check(self):
        self.ensure_one()
        if self.adjustment_type == "zone" and not self.operating_unit_ids:
            raise UserError("A zone premium names the branches in its zone.")

    def matches(self, line_type=None, distance_km=None, hour=None, operating_unit=None):
        """True when this premium applies to a job with these facts."""
        self.ensure_one()
        if self.applies_to != "all" and line_type and self.applies_to != line_type:
            return False
        if self.adjustment_type == "distance":
            if distance_km is None:
                return False
            return distance_km >= self.distance_from_km and (
                not self.distance_to_km or distance_km < self.distance_to_km
            )
        if self.adjustment_type == "zone":
            return bool(operating_unit) and operating_unit in self.operating_unit_ids
        if self.adjustment_type == "after_hours":
            if hour is None:
                return False
            if self.hour_from < self.hour_to:
                return self.hour_from <= hour < self.hour_to
            return hour >= self.hour_from or hour < self.hour_to  # overnight window
        return True

    def amount_on(self, base_price):
        self.ensure_one()
        base = max(float(base_price or 0.0), 0.0)
        raw = base * self.value / 100.0 if self.basis == "percent" else self.value
        return _money(raw)

    @api.model
    def premiums_for(self, kinds, base_price, on_date=None, company=None, **facts):
        """[(premium, amount)] for the declared kinds of this job (urgency,
        timing, zone, distance), each one in force on the day."""
        day = on_date or fields.Date.context_today(self)
        company = company or self.env.company
        found = self.sudo().search(
            [
                ("company_id", "=", company.id),
                ("adjustment_type", "in", list(kinds or [])),
                ("state", "in", ("active", "superseded", "retired")),
                ("valid_from", "<=", day),
                "|",
                ("valid_to", "=", False),
                ("valid_to", ">=", day),
            ]
        )
        return [(p, p.amount_on(base_price)) for p in found if p.matches(**facts)]


# =========================================================================
# Page 11 - Versioning & Approval (FR-PRC-024, BRU-PRC-16)
# =========================================================================
MASS_STATES = [
    ("draft", "Draft"),
    ("in_review", "In Review"),
    ("approved", "Approved (scheduled)"),
    ("applied", "Applied"),
    ("rolled_back", "Rolled Back"),
    ("cancelled", "Cancelled"),
]
MASS_TERMS = frozenset(
    {
        "line_type",
        "product_code_prefix",
        "category_id",
        "include_contract",
        "change_kind",
        "value",
        "effective_date",
        "reason",
        "company_id",
    }
)


class FixPriceMassChange(models.Model):
    _name = "fix.price.mass.change"
    _description = "Mass Price Change"
    _inherit = ["mail.thread", "fix.approvable.mixin"]
    _order = "id desc"

    _approval_domain = "pricing_mass_change"
    _approval_apply_method = "action_approve"
    _approval_routed = True

    name = fields.Char(readonly=True, copy=False, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    line_type = fields.Selection(
        [("all", "Every line type"), *LINE_TYPES], required=True, default="all"
    )
    product_code_prefix = fields.Char(
        string="Product Code Starts With", help="Empty = every product code."
    )
    category_id = fields.Many2one(
        "product.category",
        string="Catalogue Category",
        help="Only rates linked to a catalogue item of this category.",
    )
    include_contract = fields.Boolean(
        string="Include Contract Rates",
        help="Contract rates are negotiated (BRU-PRC-11) and stay out unless ticked.",
    )
    change_kind = fields.Selection(
        [("percent", "Percentage"), ("absolute", "Absolute amount (BDT)")],
        required=True,
        default="percent",
    )
    value = fields.Float(
        string="Change", required=True, help="+5 raises by 5% (or BDT 5); -5 lowers."
    )
    effective_date = fields.Date(required=True)
    reason = fields.Text(required=True)
    state = fields.Selection(MASS_STATES, required=True, default="draft", readonly=True)
    line_ids = fields.One2many("fix.price.mass.change.line", "change_id", readonly=True)
    line_count = fields.Integer(string="Rates Affected", compute="_compute_counts")
    below_floor_count = fields.Integer(string="Below a Floor", compute="_compute_counts")
    preview_at = fields.Datetime(string="Previewed On", readonly=True, copy=False)
    submitted_by = fields.Many2one("res.users", readonly=True, copy=False)
    approved_by = fields.Many2one("res.users", readonly=True, copy=False)
    applied_at = fields.Datetime(readonly=True, copy=False)
    rolled_back_by = fields.Many2one("res.users", readonly=True, copy=False)
    rollback_reason = fields.Text(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields() | {
            "state",
            "name",
            "preview_at",
            "submitted_by",
            "approved_by",
            "applied_at",
            "rolled_back_by",
            "rollback_reason",
        }
        return guarded

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(rec.state != "draft" for rec in self):
            locked |= MASS_TERMS
        return locked

    def _approval_pinned_fields(self) -> set:
        return super()._approval_pinned_fields() | MASS_TERMS

    @api.depends("line_ids.below_floor")
    def _compute_counts(self):
        for rec in self:
            rec.line_count = len(rec.line_ids)
            rec.below_floor_count = len(rec.line_ids.filtered("below_floor"))

    @api.constrains("change_kind", "value")
    def _check_value(self):
        for rec in self:
            if not rec.value:
                raise ValidationError("A mass change moves prices: state by how much.")
            if rec.change_kind == "percent" and rec.value <= -100.0:
                raise ValidationError("A price cannot fall by 100% or more.")

    def _immediate(self):
        self.ensure_one()
        return self.effective_date <= fields.Date.context_today(self)

    def _approval_group_xmlid(self):
        # BRU-PRC-16: an immediate mass change is the CCO's decision.
        if self and len(self) == 1 and self.effective_date and self._immediate():
            return GROUP_CCO
        return ROLE_RELEASER

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, (ROLE_OFFICER,), "Raising a mass price change")
        records = super().create(vals_list)
        for rec in records:
            rec._guarded().write(
                {"name": "MPC/%s/%05d" % (fields.Date.context_today(rec).year, rec.id)}
            )
        return records

    def write(self, vals):
        if not self._fix_guard_open():
            require_role(self.env, (ROLE_OFFICER,), "Changing a mass price change")
            touched = MASS_TERMS & set(vals)
            for rec in self:
                if rec.state != "draft" and any(
                    rec._fix_guard_differs(n, vals[n], rec[n]) for n in touched
                ):
                    raise UserError(
                        "%s is %s: its terms are pinned to what was approved."
                        % (rec.name, dict(MASS_STATES)[rec.state])
                    )
        return super().write(vals)

    # ---- preview -----------------------------------------------------------
    def _target_cards(self):
        self.ensure_one()
        domain = [("state", "=", "released"), ("company_id", "=", self.company_id.id)]
        if self.line_type != "all":
            domain.append(("line_type", "=", self.line_type))
        if self.product_code_prefix:
            domain.append(("product_code", "=like", self.product_code_prefix.strip() + "%"))
        if self.category_id:
            domain.append(("catalogue_item_id.category_id", "child_of", self.category_id.id))
        if not self.include_contract:
            domain.append(("min_tier", "!=", 99))
        return self.env["fix.rate.card"].sudo().search(domain)

    def _new_price(self, current):
        self.ensure_one()
        if self.change_kind == "percent":
            return _money(current * (1.0 + self.value / 100.0))
        return _money(current + self.value)

    def action_preview(self):
        """Lists every released rate the change touches, with its new price
        and the floor it must stay above (FR-PRC-024 preview)."""
        require_role(self.env, (ROLE_OFFICER,), "Previewing a mass price change")
        Line = self.env["fix.price.mass.change.line"].sudo()
        Floor = self.env["fix.price.floor"].sudo()
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a Draft mass change is previewed.")
            rec.line_ids.sudo().unlink()
            rows = []
            for card in rec._target_cards():
                floors = Floor.search(
                    [("product_code", "=", card.product_code), ("active", "=", True)]
                )
                floor = max(floors.mapped("floor_price") or [0.0])
                new = rec._new_price(card.unit_price)
                rows.append(
                    {
                        "change_id": rec.id,
                        "rate_card_id": card.id,
                        "current_price": card.unit_price,
                        "new_price": new,
                        "floor_price": floor,
                    }
                )
            Line.create(rows)
            rec._guarded().write({"preview_at": fields.Datetime.now()})
        return True

    def _check_preview(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError("Preview the change first: it touches no released rate.")
        broken = self.line_ids.filtered(lambda line: line.new_price <= 0 or line.below_floor)
        if broken:
            raise UserError(
                "%d rate(s) would fall to zero or below their floor (e.g. %s); "
                "margin-floor compliance fails (spec §8.1)." % (len(broken), broken[0].product_code)
            )
        moved = self.line_ids.filtered(
            lambda line: line.rate_card_id.state != "released"
            or abs(line.rate_card_id.unit_price - line.current_price) > 0.005
        )
        if moved:
            raise UserError(
                "%s changed since the preview; preview again." % moved[0].rate_card_id.name
            )

    def action_request_approval(self, justification=None):
        require_role(self.env, (ROLE_OFFICER,), "Submitting a mass price change")
        for rec in self:
            resubmit = rec.state == "in_review" and rec.approval_state in ("none", "returned")
            if rec.state != "draft" and not resubmit:
                raise UserError("Only a Draft mass change is submitted.")
            if rec.state == "draft":
                rec.action_preview()
            rec._check_preview()
            rec._guarded().write({"state": "in_review", "submitted_by": self.env.uid})
        return super().action_request_approval(justification=justification)

    def action_submit(self):
        return self.action_request_approval()

    def action_approve(self):
        """From the M63 inbox: a Price-Book Releaser (the CCO for an immediate
        change) who did not raise it. Applies at once when the date has come."""
        self._approval_assert_routed()
        authority = self._approval_authority_user()
        acting = self._approval_acting_users()
        for rec in self:
            if rec.state != "in_review":
                raise UserError("Only a mass change In Review is approved.")
            if rec._immediate():
                if not (self.env.su or authority.has_group(GROUP_CCO)):
                    raise AccessError(
                        "An immediate mass price change needs CCO approval (BRU-PRC-16)."
                    )
                if not self.env.su and acting & (rec.create_uid | rec.submitted_by):
                    raise UserError(
                        "Segregation of duties: you raised or submitted %s (BRU-PRC-07)." % rec.name
                    )
            else:
                require_releaser_not_author(
                    self.env,
                    authority,
                    acting,
                    rec,
                    rec.create_uid | rec.submitted_by,
                    "Approving a mass price change",
                )
            rec._check_preview()
            rec._guarded().write({"state": "approved", "approved_by": self.env.uid})
            if rec._immediate():
                rec._apply()
        return True

    def _approval_on_rejected(self, comment):
        self.filtered(lambda r: r.state == "in_review")._guarded().write({"state": "draft"})
        return super()._approval_on_rejected(comment)

    def action_recall_approval(self):
        result = super().action_recall_approval()
        self.filtered(lambda r: r.state == "in_review")._guarded().write({"state": "draft"})
        return result

    def action_cancel(self):
        require_role(self.env, (ROLE_OFFICER,), "Cancelling a mass price change")
        for rec in self:
            if rec.state not in ("draft", "approved"):
                raise UserError(
                    "Only a Draft or a scheduled (not yet applied) change is cancelled."
                )
            rec._guarded().write({"state": "cancelled"})
        return True

    def _publish(self, card, old, new):
        publish(
            self.env,
            "pricing.price_changed",
            "fix.rate.card",
            card.id,
            {
                "target_model": "fix.rate.card",
                "target_id": card.id,
                "product_code": card.product_code or "",
                "change_type": "change",
                "old_value": old,
                "new_value": new,
                "approved_by_id": self.approved_by.id or self.env.uid,
            },
        )

    def _apply(self):
        """Approved -> Applied: every previewed rate moves, all or nothing."""
        for rec in self:
            if rec.state != "approved":
                continue
            rec._check_preview()
            for line in rec.line_ids:
                line.rate_card_id._guarded().write({"unit_price": line.new_price})
                rec._publish(line.rate_card_id, line.current_price, line.new_price)
            rec.line_ids.sudo().write({"applied": True})
            rec._guarded().write({"state": "applied", "applied_at": fields.Datetime.now()})
            rec.message_post(body="Applied to %d rate(s)." % len(rec.line_ids))

    @api.model
    def cron_apply_due(self):
        """Scheduled activation: approved changes whose date has come."""
        due = self.search(
            [("state", "=", "approved"), ("effective_date", "<=", fields.Date.context_today(self))]
        )
        due._apply()
        return len(due)

    def action_rollback(self, reason=None):
        """One-step rollback (FR-PRC-024): every rate goes back to the price it
        had, if nothing else moved it since. Decided by a Price-Book Releaser."""
        require_role(
            self.env,
            (ROLE_RELEASER,),
            "Rolling back a mass price change",
            role="Price-Book Releaser",
        )
        if not (reason or "").strip():
            raise UserError("State why the mass change is rolled back.")
        for rec in self:
            if rec.state != "applied":
                raise UserError("Only an applied mass change is rolled back.")
            moved = rec.line_ids.filtered(
                lambda line: abs(line.rate_card_id.unit_price - line.new_price) > 0.005
            )
            if moved:
                raise UserError(
                    "%s was changed again after this mass change; roll that back first."
                    % moved[0].rate_card_id.name
                )
            for line in rec.line_ids:
                line.rate_card_id._guarded().write({"unit_price": line.current_price})
                rec._publish(line.rate_card_id, line.new_price, line.current_price)
            rec._guarded().write(
                {
                    "state": "rolled_back",
                    "rolled_back_by": self.env.uid,
                    "rollback_reason": reason.strip(),
                }
            )
            rec.message_post(body="Rolled back: %s" % reason.strip())
        return True


class FixPriceMassChangeLine(models.Model):
    """One rate the mass change touches: system-written by the preview."""

    _name = "fix.price.mass.change.line"
    _description = "Mass Price Change Line"
    _order = "change_id, product_code"

    change_id = fields.Many2one(
        "fix.price.mass.change", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="change_id.company_id", store=True)
    currency_id = fields.Many2one(related="change_id.currency_id")
    rate_card_id = fields.Many2one("fix.rate.card", required=True, ondelete="restrict")
    product_code = fields.Char(related="rate_card_id.product_code", store=True)
    line_type = fields.Selection(related="rate_card_id.line_type", store=True)
    current_price = fields.Monetary(string="Price Now")
    new_price = fields.Monetary(string="New Price")
    floor_price = fields.Monetary(string="Floor")
    below_floor = fields.Boolean(compute="_compute_below", store=True)
    applied = fields.Boolean(readonly=True)

    @api.depends("new_price", "floor_price")
    def _compute_below(self):
        for line in self:
            line.below_floor = bool(line.floor_price and line.new_price + 0.005 < line.floor_price)


# =========================================================================
# Page 5 - Contract Pricing: the rate names its M08 contract (FR-PRC-016)
# =========================================================================
class FixRateCardContract(models.Model):
    _inherit = "fix.rate.card"

    contract_id = fields.Many2one(
        "fix.contract",
        string="Contract (M08)",
        index=True,
        ondelete="restrict",
        help="The signed contract this negotiated rate belongs to. The rate prices only "
        "that contract's work, only within its term (BRU-PRC-11, AC-08).",
    )

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields()
        if any(card.state != "draft" for card in self):
            guarded |= {"contract_id"}
        return guarded

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(card.state != "draft" for card in self):
            locked |= {"contract_id"}
        return locked

    @api.model
    def _contract_vals(self, vals):
        """A contract rate is keyed by its contract: the lane, the number and
        (when left empty) the window follow the contract."""
        Contract = self.env["fix.contract"].sudo()
        contract = (
            Contract.browse(vals.get("contract_id")).exists() if vals.get("contract_id") else None
        )
        if not contract and vals.get("contract_no") and int(vals.get("min_tier") or 0) == 99:
            contract = Contract.search([("code", "=", vals["contract_no"].strip())], limit=1)
            if contract:
                vals["contract_id"] = contract.id
        if contract:
            vals["contract_no"] = contract.code
            vals["min_tier"] = 99
            if not vals.get("valid_from"):
                vals["valid_from"] = contract.date_start
            if not vals.get("valid_to"):
                vals["valid_to"] = contract.date_end
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._contract_vals(vals)
            if (
                int(vals.get("min_tier") or 0) == 99
                and vals.get("contract_no")
                and not vals.get("contract_id")
            ):
                raise UserError(
                    "A contract rate names its M08 contract (FR-PRC-016); no contract %s "
                    "exists." % (vals.get("contract_no") or "")
                )
        return super().create(vals_list)

    def write(self, vals):
        if "contract_id" in vals and not self._fix_guard_open():
            vals = dict(vals)
            if vals["contract_id"]:
                contract = self.env["fix.contract"].sudo().browse(vals["contract_id"])
                vals.update({"contract_no": contract.code, "min_tier": 99})
        return super().write(vals)

    @api.constrains("contract_id", "valid_from", "valid_to", "contract_no", "company_id")
    def _check_contract_term(self):
        for card in self.filtered("contract_id"):
            contract = card.contract_id.sudo()
            if card.contract_no != contract.code:
                raise UserError("The contract number is the contract's own (%s)." % contract.code)
            if contract.company_id and contract.company_id != card.company_id:
                raise UserError("The contract belongs to another company.")
            if (card.valid_from and card.valid_from < contract.date_start) or (
                card.valid_to and card.valid_to > contract.date_end
            ):
                raise UserError(
                    "A contract rate lives within the contract's term (%s to %s)."
                    % (contract.date_start, contract.date_end)
                )

    @api.model
    def _resolve(self, product_code, tier=0, contract_no=None, on_date=None):
        """The contract lane lapses with its contract (AC-08): a rate whose
        contract is not in force on the day is skipped, and the customer falls
        back to the tier rate."""
        card = super()._resolve(product_code, tier=tier, contract_no=contract_no, on_date=on_date)
        if card and card.min_tier == 99 and card.contract_id:
            day = on_date or fields.Date.context_today(self)
            contract = card.contract_id.sudo()
            live = contract.state in ("active", "expiring") and (
                contract.date_start <= day <= contract.date_end
            )
            if not live:
                return super()._resolve(product_code, tier=tier, contract_no=None, on_date=on_date)
        return card


# =========================================================================
# Pages 1 / 10 - the simulation asks its questions as fields, not JSON
# =========================================================================
class FixPriceSimulationInputs(models.Model):
    _inherit = "fix.price.simulation"

    quantity = fields.Float(default=1.0)
    customer_tier = fields.Integer(string="Customer Tier")
    contract_id = fields.Many2one("fix.contract", string="Contract (M08)")
    channel = fields.Selection(
        [("portal", "Customer portal"), ("branch", "Branch"), ("corporate", "Corporate")],
        string="Sales Channel",
    )
    proposed_price = fields.Monetary(
        string="Price to Test",
        currency_field="currency_id",
        help="Optional: is it below the floor?",
    )
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.ref("base.BDT", raise_if_not_found=False)
    )
    premium_kinds = fields.Char(
        string="Premiums",
        help="Comma-separated: express, emergency, after_hours, weekend, holiday.",
    )

    def _inputs(self):
        data = dict(super()._inputs())
        # the field's default (1) never overrides a quantity the older JSON
        # input already states
        if self.quantity and (self.quantity != 1.0 or "quantity" not in data):
            data["quantity"] = self.quantity
        if self.customer_tier:
            data["customer_tier"] = self.customer_tier
        if self.contract_id:
            data["contract_no"] = self.contract_id.code
        if self.channel:
            data["channel"] = self.channel
        if self.proposed_price:
            data["price"] = self.proposed_price
        return data

    def action_compute(self):
        """The engine's result, plus the declared premiums and the item's
        promotions as named lines (BRU-PRC-02)."""
        result = super().action_compute()
        Premium = self.env["fix.price.adjustment"]
        for rec in self:
            out = json.loads(rec.result_json or "{}")
            kinds = [k.strip() for k in (rec.premium_kinds or "").split(",") if k.strip()]
            if kinds:
                card = self.env["fix.rate.card"].sudo().browse(out.get("rate_card_id"))
                lines = Premium.premiums_for(
                    kinds, out.get("unit_price") or 0.0, line_type=card.line_type or None
                )
                out["premiums"] = [{"code": p.code, "amount": amount} for p, amount in lines]
                extra = round(sum(a for _p, a in lines), 2)
                out["net_unit_price"] = round(out["net_unit_price"] + extra, 2)
                out["net_total"] = round(out["net_unit_price"] * out["quantity"], 2)
                rec._guarded().write({"result_json": json.dumps(out, sort_keys=True)})
        return result


# =========================================================================
# Page 8 - a promotion names the items it prices (FR-PRC-037)
# =========================================================================
class FixPromotionScope(models.Model):
    _inherit = "fix.promotion"

    catalogue_item_ids = fields.Many2many(
        "fix.catalogue.item",
        "fix_promotion_catalogue_item_rel",
        "promotion_id",
        "item_id",
        string="Items It Applies To",
        help="Empty = every item. A promotion for named items never discounts another one.",
    )

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(rec.state != "draft" for rec in self):
            locked |= {"catalogue_item_ids"}
        return locked

    def write(self, vals):
        if "catalogue_item_ids" in vals and not self._fix_guard_open():
            for rec in self:
                if rec.state != "draft":
                    raise UserError(
                        "%s is %s: the items it applies to cannot change any more."
                        % (rec.display_name, dict(rec._fields["state"].selection)[rec.state])
                    )
        return super().write(vals)

    def _item_codes(self):
        self.ensure_one()
        return set(
            filter(None, self.catalogue_item_ids.sudo().mapped("product_tmpl_id.default_code"))
        )

    def covers(self, product_code=None):
        """True when this promotion may discount `product_code`."""
        self.ensure_one()
        if not self.catalogue_item_ids:
            return True
        return bool(product_code) and product_code in self._item_codes()

    @api.model
    def best_combination(self, promotions, base_price, channel=None, product_code=None):
        scoped = promotions.filtered(lambda p: p.covers(product_code))
        return super().best_combination(scoped, base_price, channel=channel)
