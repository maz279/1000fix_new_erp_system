# fix_capex_po — the M16 purchase order of a capex item (A08 M49-10, spec §8
# step 3 "Commitment: PO raised in M16 carrying the capex reference").
#
# Before: nothing linked a capex request to the order that spends it, so a
# capital purchase could be ordered with no approved capex and an approved
# capex could be ordered several times over. A capital PO now names its
# APPROVED capex request, the orders against one request never exceed its
# approved amount, and the link is frozen once the order leaves draft. The
# bills of that PO book their cost to the capex's CWIP project
# (cd_asset_finance_hse_bridge, the M52 -> M49 hand-off).
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_asset_common import money

OPEN_PO_STATES = ("draft", "sent", "acknowledged", "partially_received", "received", "closed")


class FixPurchaseOrderCapex(models.Model):
    _inherit = "fix.purchase.order"

    is_capex = fields.Boolean(
        string="Capital Purchase",
        tracking=True,
        help="A capital item: the order names the approved capex request it spends",
    )
    capex_request_id = fields.Many2one(
        "fix.capex.request",
        string="Capex Request",
        index=True,
        tracking=True,
        domain="[('state', 'in', ('approved', 'cwip')), ('company_id', '=', company_id)]",
        ondelete="restrict",
    )

    _CAPEX_TERMS = frozenset({"is_capex", "capex_request_id"})

    def _approval_pinned_fields(self) -> set:
        return super()._approval_pinned_fields() | set(self._CAPEX_TERMS)

    def write(self, vals):
        if self and not self.env.su and set(vals) & self._CAPEX_TERMS:
            issued = self.filtered(lambda po: po.state != "draft")
            if any(
                po._fields[n].convert_to_record(po._fields[n].convert_to_cache(vals[n], po), po)
                != po[n]
                for po in issued
                for n in set(vals) & self._CAPEX_TERMS
            ):
                raise UserError(
                    self.env._("%s is issued: its capex reference is frozen.", issued[:1].name)
                )
        return super().write(vals)

    @api.constrains("capex_request_id", "is_capex", "company_id")
    def _check_capex_link(self):
        for po in self:
            req = po.capex_request_id.sudo()
            if not req:
                continue
            if req.company_id != po.company_id:
                raise ValidationError(self.env._("The capex request belongs to another company."))
            if req.state not in ("approved", "cwip"):
                raise ValidationError(
                    self.env._(
                        "%s is %s: a capital order references an APPROVED capex request.",
                        req.name,
                        req.state,
                    )
                )

    def _fix_assert_capex(self):
        """A capital order names an approved capex request and stays within
        its approved amount, counting every other open order against it."""
        for po in self:
            req = po.capex_request_id.sudo()
            if po.is_capex and not req:
                raise UserError(
                    self.env._(
                        "%s is a capital purchase: name the approved capex request it spends.",
                        po.name or po.display_name,
                    )
                )
            if not req:
                continue
            req._fix_assert_approved("Ordering %s" % (po.name or po.display_name))
            if req.state == "capitalised":
                raise UserError(self.env._("%s is already capitalised.", req.name))
            others = self.sudo().search(
                [
                    ("capex_request_id", "=", req.id),
                    ("id", "!=", po.id),
                    ("state", "in", OPEN_PO_STATES),
                ]
            )
            committed = money(sum(others.mapped("amount_total")) + (po.amount_total or 0.0))
            if committed > money(req.amount) + 0.005:
                raise UserError(
                    self.env._(
                        "Orders against %s would total %s, above its approved %s: raise a "
                        "supplementary capex request.",
                        req.name,
                        committed,
                        req.amount,
                    )
                )

    def action_request_approval(self, justification=None):
        self._fix_assert_capex()
        return super().action_request_approval(justification=justification)

    def action_send(self):
        self._fix_assert_capex()
        return super().action_send()


class FixCapexRequestOrders(models.Model):
    _inherit = "fix.capex.request"

    purchase_order_ids = fields.One2many(
        "fix.purchase.order", "capex_request_id", string="Purchase Orders", readonly=True
    )
    ordered_amount = fields.Monetary(
        string="Ordered", compute="_compute_ordered_amount", help="Open M16 orders against it"
    )

    @api.depends("purchase_order_ids.amount_total", "purchase_order_ids.state")
    def _compute_ordered_amount(self):
        for rec in self:
            orders = rec.sudo().purchase_order_ids.filtered(lambda po: po.state in OPEN_PO_STATES)
            rec.ordered_amount = money(sum(orders.mapped("amount_total")))
