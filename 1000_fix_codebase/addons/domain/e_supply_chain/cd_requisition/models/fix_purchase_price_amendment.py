# fix_purchase_price_amendment — A06 P11 (BRU-PRO-08 vs M52 BRU-APE-03).
#
# A genuine price change discovered after the goods arrived (a supplier's
# documented increase, a mis-keyed order price) had no route: a sent PO is
# locked, a change order is refused once anything is received, and the
# three-way match blocks the bill for good. The auditor's recommendation (owner
# question O1, not asked; the lead took it): a VERSIONED, RE-APPROVED price
# amendment of the received order line - never a match override.
#
#   - a buyer proposes the new unit price of one received line, with the reason
#     and the supplier's evidence;
#   - a holder of the DOFA tier the order's amended value needs, who is not the
#     proposer, the buyer or the requester, approves it;
#   - the approval writes the line's approved price (the match basis) and its
#     price, numbers the version and publishes po.amended. Bills already
#     approved are untouched; the goods' receipt value stays what it was, so the
#     bill's difference to the receipt is price variance (cd_ap_ext).
from odoo import api, fields, models
from odoo.addons.cd_entity_config.models.fix_dofa import TIER_GROUP
from odoo.exceptions import UserError

from libs.py.fix_events import publish  # FF-28

from .fix_requisition import GROUP_BUYER, procurement_ladder, require_role

AMENDABLE_PO_STATES = ("partially_received", "received", "closed")


class FixPurchasePriceAmendment(models.Model):
    _name = "fix.purchase.price.amendment"
    _description = "PO Price Amendment (post-receipt, re-approved)"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(readonly=True, copy=False, default="New")
    po_line_id = fields.Many2one(
        "fix.purchase.order.line",
        string="Order Line",
        required=True,
        index=True,
        ondelete="restrict",
    )
    purchase_order_id = fields.Many2one(
        related="po_line_id.order_id", store=True, index=True, string="Purchase Order"
    )
    company_id = fields.Many2one(related="po_line_id.order_id.company_id", store=True, index=True)
    currency_id = fields.Many2one(related="po_line_id.order_id.currency_id")
    product_id = fields.Many2one(related="po_line_id.product_id", string="Product")
    old_price = fields.Monetary(
        string="Approved Price Before", currency_field="currency_id", readonly=True, copy=False
    )
    new_price = fields.Monetary(
        string="Amended Unit Price", currency_field="currency_id", required=True
    )
    reason = fields.Text(required=True)
    evidence_ref = fields.Char(
        string="Supplier Evidence",
        help="The supplier's revised quotation, debit note or letter this rests on.",
    )
    version = fields.Integer(readonly=True, copy=False)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Awaiting Approval"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )
    required_tier = fields.Char(string="Approval Tier", readonly=True, copy=False)
    requested_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    decided_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    decided_at = fields.Datetime(readonly=True, copy=False)
    decision_note = fields.Char(readonly=True, copy=False)

    STAMPS = {
        "name",
        "old_price",
        "version",
        "state",
        "required_tier",
        "requested_by_id",
        "decided_by_id",
        "decided_at",
        "decision_note",
    }
    TERMS = ("po_line_id", "new_price", "reason", "evidence_ref")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self.STAMPS

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= set(self.TERMS)
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, GROUP_BUYER, "Proposing a PO price amendment")
        records = super().create(vals_list)
        for rec in records:
            line = rec.po_line_id.sudo()
            rec._guarded().write(
                {
                    "name": "%s/PA%d" % (line.order_id.name or "PO", rec.id),
                    "old_price": line.approved_unit_price or line.unit_price,
                }
            )
        return records

    def write(self, vals):
        terms = set(self.TERMS) & set(vals)
        if terms and not self._fix_guard_has_token() and any(r.state != "draft" for r in self):
            raise UserError("A submitted price amendment is fixed; reject it and propose again.")
        return super().write(vals)

    def unlink(self):
        if any(r.state != "draft" for r in self):
            raise UserError("A submitted or decided price amendment is a record.")
        return super().unlink()

    # ---- checks -------------------------------------------------------------
    def _a06_amended_total_bdt(self):
        """The order's value in BDT with this line at the amended price."""
        self.ensure_one()
        order = self.po_line_id.order_id.sudo()
        total = sum(
            (self.new_price if line == self.po_line_id else line.unit_price) * line.qty_ordered
            for line in order.line_ids
        )
        return round(total * order._fix_rate_bdt(), 2)

    def _a06_tier(self):
        amount = self._a06_amended_total_bdt()
        for bound, tier in procurement_ladder(self.env):
            if amount <= bound:
                return tier
        return "tier_5"

    def _a06_conflicted(self):
        self.ensure_one()
        order = self.purchase_order_id.sudo()
        reqs = order._fix_all_requisitions()
        return (
            self.sudo().create_uid
            | self.sudo().requested_by_id
            | order.buyer_id
            | order.create_uid
            | reqs.requested_by.user_id
        )

    # ---- actions ------------------------------------------------------------
    def action_submit(self):
        for rec in self:
            require_role(self.env, GROUP_BUYER, "Submitting a PO price amendment")
            if rec.state != "draft":
                raise UserError("Amendment %s is %s." % (rec.name, rec.state))
            line = rec.po_line_id.sudo()
            order = line.order_id
            if order.state not in AMENDABLE_PO_STATES or not line.qty_received:
                raise UserError(
                    "A price amendment revises a line that has been received (PO %s is %s). "
                    "Before receipt, raise a change order." % (order.name, order.state)
                )
            if rec.new_price < 0 or abs(rec.new_price - rec.old_price) < 0.005:
                raise UserError(
                    "Amendment %s does not change the approved price %.2f."
                    % (rec.name, rec.old_price)
                )
            if len((rec.reason or "").strip()) < 10 or not (rec.evidence_ref or "").strip():
                raise UserError(
                    "State why the price changed and the supplier evidence it rests on."
                )
            rec._guarded().write(
                {
                    "state": "submitted",
                    "requested_by_id": self.env.uid,
                    "required_tier": rec._a06_tier(),
                }
            )
        return True

    def action_approve(self, note=None):
        """Re-approval on the procurement DOFA ladder by the amended value."""
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Approve a submitted amendment (%s is %s)." % (rec.name, rec.state))
            tier = rec._a06_tier()
            group = TIER_GROUP.get(tier)
            if not self.env.su:
                if self.env.user in rec._a06_conflicted():
                    raise UserError(
                        "Segregation of duties: you proposed amendment %s or raised or requested "
                        "its order; another approver decides it." % rec.name
                    )
                if tier != "tier_0" and not (group and self.env.user.has_group(group)):
                    raise UserError(
                        "Amendment %s takes PO %s to BDT %.2f, which needs %s approval."
                        % (
                            rec.name,
                            rec.purchase_order_id.name,
                            rec._a06_amended_total_bdt(),
                            tier.replace("_", " "),
                        )
                    )
            line = rec.po_line_id.sudo()
            version = (
                self.sudo().search_count([("po_line_id", "=", line.id), ("state", "=", "approved")])
                + 1
            )
            # written as the system after the checks above: the tier holder
            # need not hold the buyer's write rights on the order
            line._guarded().write(
                {"approved_unit_price": rec.new_price, "unit_price": rec.new_price}
            )
            rec.sudo()._guarded().write(
                {
                    "state": "approved",
                    "version": version,
                    "decided_by_id": self.env.uid,
                    "decided_at": fields.Datetime.now(),
                    "decision_note": (note or "").strip() or False,
                }
            )
            order = line.order_id
            order.sudo().message_post(
                body="Price of %s amended from %.2f to %.2f (amendment %s, version %d): %s"
                % (
                    line.product_id.display_name,
                    rec.old_price,
                    rec.new_price,
                    rec.name,
                    version,
                    rec.reason.strip(),
                )
            )
            publish(
                self.env,
                "po.amended",
                "fix.purchase.order",
                order.id,
                {
                    "po_ref": order.name,
                    "po_line_id": line.id,
                    "product_id": line.product_id.id,
                    "old_price": rec.old_price,
                    "new_price": rec.new_price,
                    "currency": order.currency_id.name,
                    "version": version,
                },
            )
            order._a06_notify_vendor(
                "Purchase order %s: the price of %s is amended to %s %.2f (version %d)."
                % (
                    order.name,
                    line.product_id.display_name,
                    order.currency_id.name,
                    rec.new_price,
                    version,
                )
            )
            # bills awaiting approval are matched again at the amended price
            if "fix.vendor.invoice" in self.env:
                bills = (
                    self.env["fix.vendor.invoice"]
                    .sudo()
                    .search(
                        [
                            ("requisition_id", "=", order.id),
                            ("approval_state", "in", ("draft", "to_approve", "rejected")),
                        ]
                    )
                )
                Bill = self.env["fix.vendor.invoice"]
                for name in ("match_state", "match_detail"):
                    self.env.add_to_compute(Bill._fields[name], bills)
        return True

    def action_reject(self, note=None):
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Reject a submitted amendment (%s is %s)." % (rec.name, rec.state))
            if not self.env.su and self.env.user in (rec.requested_by_id | rec.create_uid):
                raise UserError("Segregation of duties: the proposer does not decide it.")
            if not (note or "").strip():
                raise UserError("State why amendment %s is rejected." % rec.name)
            rec.sudo()._guarded().write(
                {
                    "state": "rejected",
                    "decided_by_id": self.env.uid,
                    "decided_at": fields.Datetime.now(),
                    "decision_note": note.strip(),
                }
            )
        return True
