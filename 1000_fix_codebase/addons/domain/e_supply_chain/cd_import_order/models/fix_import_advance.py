# fix_import_advance — M44 advance payment control (A06 scorecard 24).
#
# A B/L could be received with no LC and no recorded payment instrument. An
# advance to the supplier is recorded here against its order, with the bank and
# the advance-payment guarantee, and decided by an Import Approver who did not
# request it. The B/L gate (fix.import.order._import_check_instrument) reads the
# approved advances.
#
# The cap is cd_import_order.advance_cap_pct, a share of the order's invoice
# value; the default 0 means no advance goes through unexplained: an approval
# that takes the order's advances above the cap needs a stated reason. Advances
# never exceed the invoice value. This records the instrument; the money moves
# and posts through treasury, not here.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_import_common import (
    APPROVER,
    OFFICER,
    PARAM_ADVANCE_CAP,
    param_float,
    refuse_locked,
    require_group,
    require_other_person,
)

ADVANCE_TERMS = ("order_id", "currency_id", "amount", "bank", "guarantee_ref", "purpose")


class FixImportAdvance(models.Model):
    _name = "fix.import.advance"
    _description = "Import Advance Payment"
    _order = "create_date desc, id desc"
    _inherit = ["fix.guarded.mixin", "mail.thread"]

    name = fields.Char(required=True, default="New", copy=False)
    order_id = fields.Many2one(
        "fix.import.order", string="Import Order", required=True, ondelete="restrict", index=True
    )
    company_id = fields.Many2one(related="order_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="order_id.operating_unit_id", store=True, index=True
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(currency_field="currency_id", required=True, tracking=True)
    bank = fields.Char(string="Remitting Bank", required=True)
    guarantee_ref = fields.Char(string="Advance Guarantee Reference", required=True)
    purpose = fields.Char(string="Purpose")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("requested", "Requested"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="draft",
        tracking=True,
    )
    requested_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    requested_on = fields.Datetime(readonly=True, copy=False)
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True, copy=False)
    decided_on = fields.Datetime(readonly=True, copy=False)
    decision_reason = fields.Char(readonly=True, copy=False)
    above_cap = fields.Boolean(
        string="Above the Cap at Approval",
        readonly=True,
        copy=False,
        help="The approval took the order's advances above cd_import_order.advance_cap_pct.",
    )

    _amount_positive = models.Constraint("CHECK (amount > 0)", "An advance must be positive")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "requested_by_id",
            "requested_on",
            "decided_by_id",
            "decided_on",
            "decision_reason",
            "above_cap",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state != "draft":
            locked |= set(ADVANCE_TERMS)
        return locked

    @api.constrains("order_id", "currency_id")
    def _check_currency(self):
        for rec in self.sudo():
            bdt = rec.env.ref("base.BDT")
            if rec.currency_id not in (bdt, rec.order_id.currency_id):
                raise ValidationError(
                    "Record the advance in BDT or the order currency %s."
                    % rec.order_id.currency_id.name
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.import.advance") or "IADV/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        refuse_locked(
            self,
            vals,
            lambda r: set(ADVANCE_TERMS) if r.state != "draft" else set(),
            "a requested advance is fixed; cancel it and record a new one.",
        )
        return super().write(vals)

    # ---- figures -----------------------------------------------------------------
    def _advance_in_order_ccy(self):
        self.ensure_one()
        return self.order_id._to_order_ccy(self.amount or 0.0, self.currency_id)

    def _advance_total_with_approved(self):
        """This advance plus the order's approved ones, in the order currency."""
        self.ensure_one()
        others = self.sudo().search(
            [
                ("order_id", "=", self.order_id.id),
                ("state", "=", "approved"),
                ("id", "!=", self.id),
            ]
        )
        return sum(o._advance_in_order_ccy() for o in others) + self._advance_in_order_ccy()

    # ---- transitions ---------------------------------------------------------------
    def action_request(self):
        require_group(self.env, OFFICER, "Requesting an import advance")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Request a draft advance.")
            rec.order_id._import_check_fx("Requesting advance %s" % rec.name)
            rec._guarded().write(
                {
                    "state": "requested",
                    "requested_by_id": rec.env.user.id,
                    "requested_on": fields.Datetime.now(),
                }
            )
        return True

    def action_approve(self, reason=None):
        require_group(self.env, APPROVER, "Approving an import advance")
        pct = param_float(self.env, PARAM_ADVANCE_CAP, 0.0)
        for rec in self:
            if rec.state != "requested":
                raise UserError("Approve a requested advance (%s is %s)." % (rec.name, rec.state))
            require_other_person(rec.env, rec, "Advance %s" % rec.name, rec.requested_by_id)
            order = rec.order_id
            value = order._invoice_value()
            total = rec._advance_total_with_approved()
            if total > value + 0.01:
                raise UserError(
                    "Advances on %s would total %.2f, above the order's invoice value %.2f."
                    % (order.name, total, value)
                )
            above = total > value * pct / 100.0 + 0.01
            why = (reason or "").strip()
            if above and not why:
                raise UserError(
                    "Advances on %s would total %.2f %s against a cap of %.2f%% of %.2f "
                    "(%s): state why this one is approved."
                    % (order.name, total, order.currency_id.name, pct, value, PARAM_ADVANCE_CAP)
                )
            rec._guarded().write(
                {
                    "state": "approved",
                    "decided_by_id": rec.env.user.id,
                    "decided_on": fields.Datetime.now(),
                    "decision_reason": why or False,
                    "above_cap": above,
                }
            )
        return True

    def action_reject(self, reason=None):
        require_group(self.env, APPROVER, "Rejecting an import advance")
        for rec in self:
            if rec.state != "requested":
                raise UserError("Reject a requested advance.")
            why = (reason or "").strip()
            if not why:
                raise UserError("State why the advance is rejected.")
            rec._guarded().write(
                {
                    "state": "rejected",
                    "decided_by_id": rec.env.user.id,
                    "decided_on": fields.Datetime.now(),
                    "decision_reason": why,
                }
            )
        return True

    def action_cancel(self):
        require_group(self.env, OFFICER, "Cancelling an import advance")
        for rec in self:
            if rec.state not in ("draft", "requested"):
                raise UserError(
                    "Only an undecided advance is cancelled (%s is %s)." % (rec.name, rec.state)
                )
            rec._guarded().write({"state": "cancelled"})
        return True


class FixImportOrderAdvance(models.Model):
    _inherit = "fix.import.order"

    advance_ids = fields.One2many("fix.import.advance", "order_id", string="Advances")
