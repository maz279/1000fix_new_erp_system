# fix_dynamic_pricing — M11 W7: dynamic pricing rules with audit explanations (P10-M05 / R08-M03).
#
# A04 audit (2026-11-04) M11-7: a clerk created a -100% rule with a corridor
# he declared himself, which priced an item at BDT 0, and rewrote the price
# explanation afterwards. Now:
#   - rules are authored by a Pricing Officer, inside the policy corridor
#     (BRU-PRC-09), and never produce a price of zero or less;
#   - a rule never prices below the item's M11 floor: the engine reverts to
#     the static price instead (AUT-PRC-14);
#   - disabling a rule is any officer's guardrail; re-enabling it is a
#     Price-Book Releaser's decision, not the author's;
#   - the explanation is append-only (BRU-PRC-02).
from datetime import datetime
from decimal import ROUND_HALF_EVEN, Decimal

from odoo import api, fields, models
from odoo.addons.cd_rate_card.models.pricing_roles import (
    ROLE_OFFICER,
    ROLE_RELEASER,
    require_role,
)
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

# The corridor a dynamic rule may move a price within, around the list price
# (BRU-PRC-09). The spec leaves the width to configuration; these are the
# model's own first defaults (min -50%, max +100%), kept as the business
# default until the CCO confirms the corridor (report §7).
CORRIDOR_MIN_PARAM = "cd_dynamic_pricing.corridor_min_pct"
CORRIDOR_MAX_PARAM = "cd_dynamic_pricing.corridor_max_pct"
CORRIDOR_DEFAULT = (-50.0, 100.0)
RULE_TERMS = frozenset(
    {"adjustment_pct", "surge_multiplier", "min_adjustment", "max_adjustment", "rate_card_id"}
)


def _corridor(env):
    get = env["ir.config_parameter"].sudo().get_param
    try:
        lo = float(get(CORRIDOR_MIN_PARAM, CORRIDOR_DEFAULT[0]))
        hi = float(get(CORRIDOR_MAX_PARAM, CORRIDOR_DEFAULT[1]))
    except (TypeError, ValueError):
        lo, hi = CORRIDOR_DEFAULT
    return max(lo, -99.0), hi


class FixDynamicPriceRule(models.Model):
    """M11 W7: dynamic pricing with bounds, surge/off-peak logic, and explanations."""

    _name = "fix.dynamic.price.rule"
    _description = "Dynamic Price Rule"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    rate_card_id = fields.Many2one(
        "fix.rate.card",
        string="Rate Card Base",
        ondelete="set null",
        help="Linked base rate card from cd_rate_card",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    rule_type = fields.Selection(
        [
            ("demand_surge", "Demand Surge"),
            ("off_peak", "Off-Peak Discount"),
            ("inventory_clearance", "Inventory Clearance"),
            ("loyalty_tier", "Loyalty Tier Pricing"),
        ],
        required=True,
        default="demand_surge",
    )
    adjustment_pct = fields.Float(string="Adjustment %", default=0.0)
    surge_multiplier = fields.Float(string="Surge Multiplier", default=1.0)
    min_adjustment = fields.Float(string="Min Adjustment %", default=-50.0)
    max_adjustment = fields.Float(string="Max Adjustment %", default=100.0)
    channel = fields.Selection(
        [("marketplace", "Marketplace"), ("storefront", "Storefront"), ("both", "Both")],
        default="both",
        required=True,
    )
    active = fields.Boolean(default=True)
    disabled_reason = fields.Char(readonly=True, copy=False)
    disabled_by = fields.Many2one("res.users", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields() | {"disabled_reason", "disabled_by"}
        if self:
            guarded |= {"active"}
        return guarded

    @api.constrains("adjustment_pct", "max_adjustment", "min_adjustment")
    def _check_bounds(self):
        lo, hi = _corridor(self.env)
        for rec in self:
            if rec.adjustment_pct > rec.max_adjustment:
                raise UserError(
                    "Adjustment %s exceeds the maximum %s"
                    % (rec.adjustment_pct, rec.max_adjustment)
                )
            if rec.adjustment_pct < rec.min_adjustment:
                raise UserError(
                    "Adjustment %s below the minimum %s" % (rec.adjustment_pct, rec.min_adjustment)
                )
            # BRU-PRC-09: the corridor is the policy's, not the rule's own.
            if rec.min_adjustment < lo or rec.max_adjustment > hi:
                raise ValidationError(
                    "Rule %s declares a corridor of %s%% to %s%%; dynamic pricing may move a "
                    "price only within %s%% to %s%% (BRU-PRC-09)."
                    % (rec.name, rec.min_adjustment, rec.max_adjustment, lo, hi)
                )

    @api.constrains("adjustment_pct", "surge_multiplier")
    def _check_never_free(self):
        for rec in self:
            mult = rec.surge_multiplier if rec.surge_multiplier > 0 else 1.0
            if (1.0 + rec.adjustment_pct / 100.0) * mult <= 0.0:
                raise ValidationError("Rule %s would price an item at zero or less." % rec.name)

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, (ROLE_OFFICER,), "Creating a dynamic price rule")
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open():
            require_role(self.env, (ROLE_OFFICER,), "Changing a dynamic price rule")
        return super().write(vals)

    def action_disable(self, reason=None):
        """AUT-PRC-14 guardrail: any Pricing Officer switches a rule off."""
        require_role(self.env, (ROLE_OFFICER,), "Disabling a dynamic price rule")
        if not (reason or "").strip():
            raise UserError("State why the rule is disabled.")
        for rec in self.filtered("active"):
            rec._guarded().write(
                {"active": False, "disabled_reason": reason, "disabled_by": self.env.uid}
            )
            rec.message_post(body="Disabled by %s: %s" % (self.env.user.name, reason))
        return True

    def action_enable(self):
        """A Price-Book Releaser who neither authored nor disabled the rule
        switches it back on (BRU-PRC-07)."""
        require_role(
            self.env,
            (ROLE_RELEASER,),
            "Re-enabling a dynamic price rule",
            role="Price-Book Releaser",
        )
        for rec in self.with_context(active_test=False):
            if rec.active:
                continue
            if not self.env.su and self.env.user in (rec.create_uid | rec.disabled_by):
                raise UserError(
                    "Segregation of duties: you authored or disabled %s; another releaser "
                    "re-enables it." % rec.name
                )
            rec._guarded().write({"active": True, "disabled_reason": False, "disabled_by": False})
            rec.message_post(body="Re-enabled by %s." % self.env.user.name)
        return True

    def apply_to(self, base_price):
        """Compute adjusted dynamic price using high-precision Decimal arithmetic (FLAW-11.1)."""
        self.ensure_one()
        if base_price < 0:
            raise UserError("Base price cannot be negative")
        d_base = Decimal(str(base_price))
        d_mult = (
            Decimal(str(self.surge_multiplier)) if self.surge_multiplier > 0 else Decimal("1.0")
        )
        d_pct = Decimal(str(self.adjustment_pct)) / Decimal("100.0")
        adjusted = d_base * (Decimal("1.0") + d_pct) * d_mult
        if base_price > 0 and adjusted <= 0:
            # A04 audit M11-7 (dr_01): never a free price.
            raise UserError("Rule %s would price an item at zero or less." % self.name)
        return float(adjusted.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN))

    def _floor_for(self, product_code):
        if not product_code:
            return 0.0
        floors = self.env["fix.price.floor"].sudo().search([("product_code", "=", product_code)])
        return max(floors.mapped("floor_price") or [0.0])

    def calculate_and_explain(self, base_price, context_info=None, product_code=None):
        """Calculate dynamic price and persist audit explanation trail.

        BRU-PRC-09 / AUT-PRC-14: a dynamic price never goes below the item's
        floor; when it would, the static price applies and the explanation
        says so."""
        self.ensure_one()
        final_price = self.apply_to(base_price)
        code = product_code or self.rate_card_id.product_code
        floor = self._floor_for(code)
        guardrail = ""
        if floor and final_price + 0.005 < floor:
            guardrail = " Guardrail: %.2f is below the floor %.2f; static price applied." % (
                final_price,
                floor,
            )
            final_price = float(base_price)
        explanation_text = (
            f"Rule '{self.name}' ({self.rule_type}): adjustment {self.adjustment_pct}%, "
            f"surge mult {self.surge_multiplier}. Base: {base_price:.2f} -> Final: {final_price:.2f}. "
            f"Context: {context_info or 'Standard dispatch request'}"
        ) + guardrail
        # The explanation is the engine's record, written by the engine (sudo):
        # no user creates or edits one (BRU-PRC-02).
        explanation = (
            self.env["fix.price.explanation"]
            .sudo()
            .create(
                {
                    "name": f"EXP/{self.name}/{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "company_id": self.company_id.id,
                    "operating_unit_id": self.operating_unit_id.id
                    if self.operating_unit_id
                    else False,
                    "rule_id": self.id,
                    "base_price": base_price,
                    "final_price": final_price,
                    "rules_applied": explanation_text,
                    "model_driven": self.rule_type == "demand_surge",
                }
            )
        )
        publish(
            self.env,
            "pricing.calculated",
            "fix.dynamic.price.rule",
            self.id,
            {
                "rule_name": self.name,
                "base_price": float(base_price),
                "final_price": float(final_price),
            },
        )
        return {
            "final_price": final_price,
            "explanation_id": explanation.id,
            "text": explanation_text,
        }


class FixPriceExplanation(models.Model):
    """Every dynamic price is reconstructable — the audit trail.

    A04 audit M11-7 (dr_02): a clerk rewrote final_price on the trail. It is
    append-only: written by the engine, never edited or deleted."""

    _name = "fix.price.explanation"
    _description = "Price Explanation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    rule_id = fields.Many2one("fix.dynamic.price.rule", string="Applied Rule", ondelete="set null")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    base_price = fields.Float(string="Base Price")
    final_price = fields.Float(string="Final Price")
    rules_applied = fields.Text(string="Rules Applied")
    model_driven = fields.Boolean(string="ML Model Driven")

    _TRAIL_FIELDS = frozenset(
        {
            "company_id",
            "operating_unit_id",
            "name",
            "rule_id",
            "currency_id",
            "base_price",
            "final_price",
            "rules_applied",
            "model_driven",
        }
    )

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            raise UserError(
                "A price explanation is written by the pricing engine when it prices; "
                "it is not created by hand (BRU-PRC-02)."
            )
        return super().create(vals_list)

    def write(self, vals):
        if self._TRAIL_FIELDS & set(vals) and not self.env.su:
            raise UserError("The price explanation trail is append-only (BRU-PRC-02).")
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("The price explanation trail is append-only (BRU-PRC-02).")
        return super().unlink()

    def action_reconstruct(self):
        """Re-run the rule on the recorded base price and say whether the
        recorded final price is what the rule gives today."""
        self.ensure_one()
        if not self.rule_id:
            message, kind = "The rule behind %s no longer exists." % self.name, "warning"
        else:
            again = self.rule_id.sudo().apply_to(self.base_price)
            if abs(again - self.final_price) < 0.005 or "Guardrail" in (self.rules_applied or ""):
                message, kind = (
                    "%s reconstructs: %.2f -> %.2f."
                    % (self.name, self.base_price, self.final_price),
                    "success",
                )
            else:
                message, kind = (
                    "%s recorded %.2f, but rule %s now gives %.2f (the rule changed since)."
                    % (self.name, self.final_price, self.rule_id.name, again),
                    "warning",
                )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {"title": "Price explanation", "message": message, "type": kind},
        }
