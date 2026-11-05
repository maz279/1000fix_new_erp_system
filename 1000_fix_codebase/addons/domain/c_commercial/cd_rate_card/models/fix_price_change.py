# fix.price.change — the one way a live rate or floor changes (A04 audit,
# 2026-11-04, M11-5: rc_01 and pf_08).
#
# Any user lowered a live rate card from BDT 1,000 to 1, or a floor from
# 1,000 to 1, with no review (FR-PRC-034/035, BRU-PRC-07). A released rate
# card's price and a floor's price are now guarded: a Pricing Officer raises a
# change request (release a new rate, change a price, retire it) with a
# reason; a Price-Book Releaser who did not raise it decides it from the M63
# inbox; the change applies only if the target still carries the value the
# request was raised against.
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish

from .pricing_roles import ROLE_OFFICER, ROLE_RELEASER, require_releaser_not_author, require_role

CHANGE_STATES = [
    ("draft", "Draft"),
    ("pending", "Awaiting Release"),
    ("applied", "Applied"),
    ("rejected", "Rejected"),
    ("cancelled", "Cancelled"),
]
CHANGE_TERMS = frozenset(
    {"target_type", "change_type", "rate_card_id", "floor_id", "proposed_value", "reason"}
)


class FixPriceChange(models.Model):
    _name = "fix.price.change"
    _description = "Price Change Request"
    _inherit = ["mail.thread", "fix.approvable.mixin"]
    _order = "id desc"

    _approval_domain = "pricing_change"
    _approval_apply_method = "action_apply"
    _approval_group = ROLE_RELEASER
    _approval_routed = True

    name = fields.Char(required=True, readonly=True, copy=False, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    target_type = fields.Selection(
        [("rate_card", "Rate Card"), ("floor", "Price Floor")], required=True
    )
    change_type = fields.Selection(
        [
            ("release", "Release a new rate"),
            ("change", "Change the price"),
            ("retire", "Retire"),
        ],
        required=True,
        default="change",
    )
    rate_card_id = fields.Many2one("fix.rate.card", ondelete="restrict", index=True)
    floor_id = fields.Many2one("fix.price.floor", ondelete="restrict", index=True)
    product_code = fields.Char(compute="_compute_product_code", store=True)
    current_value = fields.Monetary(
        readonly=True, help="The target's price when the request was raised."
    )
    proposed_value = fields.Monetary(help="The new price (release/change).")
    reason = fields.Text(required=True)
    state = fields.Selection(CHANGE_STATES, required=True, default="draft", readonly=True)
    applied_by = fields.Many2one("res.users", readonly=True, copy=False)
    applied_at = fields.Datetime(readonly=True, copy=False)
    rejection_reason = fields.Text(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields() | {
            "state",
            "current_value",
            "applied_by",
            "applied_at",
            "rejection_reason",
            "name",
        }
        if any(rec.state != "draft" for rec in self):
            # the request is pinned to what was asked for
            guarded |= CHANGE_TERMS
        return guarded

    @api.depends("rate_card_id.product_code", "floor_id.product_code")
    def _compute_product_code(self):
        for rec in self:
            rec.product_code = rec.rate_card_id.product_code or rec.floor_id.product_code

    def _target(self):
        self.ensure_one()
        return self.rate_card_id if self.target_type == "rate_card" else self.floor_id

    def _target_value(self):
        self.ensure_one()
        target = self._target().sudo()
        if not target:
            return 0.0
        return target.unit_price if self.target_type == "rate_card" else target.floor_price

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, (ROLE_OFFICER,), "Raising a price change")
        records = super().create(vals_list)
        for rec in records:
            rec._guarded().write(
                {
                    "name": "PCR/%s/%05d" % (fields.Date.context_today(rec).year, rec.id),
                    "current_value": rec._target_value(),
                }
            )
        return records

    def write(self, vals):
        if not self._fix_guard_open():
            require_role(self.env, (ROLE_OFFICER,), "Changing a price change request")
        return super().write(vals)

    def _approval_amount(self) -> float:
        return self.proposed_value or 0.0

    def _validate(self):
        self.ensure_one()
        target = self._target()
        if not target:
            raise UserError("Name the rate card or floor the change is for.")
        if not (self.reason or "").strip():
            raise UserError("State why the price changes (FR-PRC-034).")
        if self.change_type in ("release", "change") and self.proposed_value <= 0:
            raise UserError("A price change needs a positive new price.")
        if self.target_type == "rate_card":
            if self.change_type == "release" and target.state != "draft":
                raise UserError("Only a Draft rate card is released.")
            if self.change_type in ("change", "retire") and target.state != "released":
                raise UserError("Only a released rate card is changed or retired.")
        else:
            if self.change_type == "release":
                raise UserError("A floor is in force from its creation; change or retire it.")
            if not target.active:
                raise UserError("The floor is retired.")
        if self.change_type == "change" and abs(self.proposed_value - self._target_value()) < 0.005:
            raise UserError("The proposed price equals the current one.")
        open_ = self.search(
            [
                ("id", "!=", self.id),
                ("state", "=", "pending"),
                ("rate_card_id" if self.target_type == "rate_card" else "floor_id", "=", target.id),
            ],
            limit=1,
        )
        if open_:
            raise UserError("%s already awaits release for this target." % open_.name)

    def action_request_approval(self, justification=None):
        require_role(self.env, (ROLE_OFFICER,), "Submitting a price change")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a Draft change is submitted.")
            rec._validate()
            rec._guarded().write({"state": "pending", "current_value": rec._target_value()})
        return super().action_request_approval(justification=justification)

    def action_submit(self):
        return self.action_request_approval()

    def action_apply(self):
        """Pending -> Applied, from the releaser's M63 inbox."""
        self._approval_assert_routed()
        authority = self._approval_authority_user()
        acting = self._approval_acting_users()
        now = fields.Datetime.now()
        for rec in self:
            if rec.state != "pending":
                raise UserError("Only a pending change is applied.")
            requester = rec.approval_request_id.sudo().requested_by_id
            require_releaser_not_author(
                self.env,
                authority,
                acting,
                rec,
                rec.create_uid | requester,
                "Releasing a price change",
            )
            if abs(rec._target_value() - rec.current_value) > 0.005:
                raise UserError(
                    "%s was raised against %.2f but the target now stands at %.2f; raise "
                    "it again." % (rec.name, rec.current_value, rec._target_value())
                )
            target = rec._target()
            old = rec._target_value()
            if rec.target_type == "rate_card":
                if rec.change_type == "release":
                    target._guarded().write(
                        {
                            "state": "released",
                            "unit_price": rec.proposed_value,
                            "released_by": self.env.uid,
                            "released_at": now,
                        }
                    )
                elif rec.change_type == "change":
                    target._guarded().write({"unit_price": rec.proposed_value})
                else:
                    target._guarded().write({"state": "retired", "active": False})
            elif rec.change_type == "change":
                target._guarded().write({"floor_price": rec.proposed_value})
            else:
                target._guarded().write({"active": False})
            rec._guarded().write(
                {"state": "applied", "applied_by": self.env.uid, "applied_at": now}
            )
            publish(
                self.env,
                "pricing.price_changed",
                rec._name,
                rec.id,
                {
                    "target_model": target._name,
                    "target_id": target.id,
                    "product_code": rec.product_code or "",
                    "change_type": rec.change_type,
                    "old_value": old,
                    "new_value": rec.proposed_value if rec.change_type != "retire" else None,
                    "approved_by_id": self.env.uid,
                },
            )
        return True

    def _approval_on_rejected(self, comment):
        self.filtered(lambda r: r.state == "pending")._guarded().write(
            {"state": "rejected", "rejection_reason": comment or False}
        )
        return super()._approval_on_rejected(comment)

    def action_recall_approval(self):
        result = super().action_recall_approval()
        self.filtered(lambda r: r.state == "pending")._guarded().write({"state": "draft"})
        return result

    def action_cancel(self):
        require_role(self.env, (ROLE_OFFICER,), "Cancelling a price change")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a Draft change is cancelled; recall a pending one first.")
            rec._guarded().write({"state": "cancelled"})
        return True
