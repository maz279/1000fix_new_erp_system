# fix_purchase_receipt — M16 goods receipt against a purchase order (A06 R5).
#
# A06 audit (2026-11-03), M16-4/6/7: the received side of the three-way match
# was a typed number on the PO line (qty_received), set with no GRN, on a
# draft or cancelled PO, by the same user who requested, approved and bought
# it; an inspection had no link to any receipt, so a 10/10 rejection left the
# goods "received" and the bill matched. Now:
#   - a receipt references the PO lines it receives, is posted by a Receiver
#     who is neither the requester nor the buyer, only on a sent or
#     acknowledged PO, and is final once posted;
#   - the PO line's received quantity is the sum of POSTED receipt lines;
#   - the inspection outcome (fix.procurement.inspection) feeds the receipt
#     line's accepted quantity, and only accepted goods are matchable
#     (BRU-PRO-11: until the inspection is recorded nothing is);
#   - goods.received carries the vendor and the dates the M42 scorecard needs.
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish  # FF-28

from .fix_requisition import (
    GROUP_RECEIVER,
    PARAM_INSPECTION,
    bool_param,
    over_receipt_ceiling,
    require_role,
)


class FixPurchaseReceipt(models.Model):
    _name = "fix.purchase.receipt"
    _description = "Purchase Goods Receipt (GRN)"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(required=True, default="New", copy=False, readonly=True)
    purchase_order_id = fields.Many2one(
        "fix.purchase.order",
        string="Purchase Order",
        required=True,
        index=True,
        ondelete="restrict",
    )
    company_id = fields.Many2one(
        related="purchase_order_id.company_id", store=True, index=True, readonly=True
    )
    operating_unit_id = fields.Many2one(
        related="purchase_order_id.operating_unit_id", store=True, readonly=True
    )
    vendor_id = fields.Many2one(
        related="purchase_order_id.vendor_id", store=True, readonly=True, string="Vendor"
    )
    delivery_note_ref = fields.Char(string="Vendor Delivery Note / Challan")
    received_on = fields.Date(readonly=True, copy=False, help="Stamped when the receipt is posted.")
    receiver_id = fields.Many2one("res.users", string="Received By", readonly=True, copy=False)
    posted_at = fields.Datetime(readonly=True, copy=False)
    state = fields.Selection(
        [("draft", "Draft"), ("posted", "Posted"), ("cancelled", "Cancelled")],
        default="draft",
        required=True,
        tracking=True,
    )
    line_ids = fields.One2many("fix.purchase.receipt.line", "receipt_id", string="Lines")
    notes = fields.Text()

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "received_on", "receiver_id", "posted_at"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= {"purchase_order_id", "delivery_note_ref", "line_ids"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.purchase.receipt") or "PGRN/New"
                )
        records = super().create(vals_list)
        for rec in records:
            rec.purchase_order_id._a06_assert_receivable()
            if not rec.line_ids:
                rec._a06_load_open_lines()
        return records

    def _a06_load_open_lines(self):
        """The receipt's lines are its PO's open lines, at what is still due: a
        receipt of another PO's line cannot be keyed, and the receiver corrects
        the delivered quantities rather than typing the order in again."""
        self.ensure_one()
        lines = [
            {
                "receipt_id": self.id,
                "po_line_id": line.id,
                "qty_received": line.qty_ordered - line.qty_received,
            }
            for line in self.purchase_order_id.sudo().line_ids
            if line.qty_ordered - line.qty_received > 1e-6
        ]
        if lines:
            self.env["fix.purchase.receipt.line"].create(lines)

    def write(self, vals):
        if not self._fix_guard_has_token():
            frozen = set(vals) - {"notes"}
            if frozen and any(r.state != "draft" for r in self):
                raise UserError("A posted goods receipt is final; only its notes can change.")
        repoint = self.browse()
        if vals.get("purchase_order_id"):
            repoint = self.filtered(lambda r: r.purchase_order_id.id != vals["purchase_order_id"])
        result = super().write(vals)
        for rec in repoint:
            rec.line_ids.unlink()
            rec.purchase_order_id._a06_assert_receivable()
            rec._a06_load_open_lines()
        return result

    def unlink(self):
        if any(r.state == "posted" for r in self):
            raise UserError("A posted goods receipt is final and cannot be deleted.")
        return super().unlink()

    def _a06_conflicted_receivers(self):
        """The requester and the buyer of the PO never receive it (SOD-02)."""
        self.ensure_one()
        order = self.purchase_order_id.sudo()
        reqs = order._fix_all_requisitions()  # A06 P40: every consolidated requester
        return order.buyer_id | order.create_uid | reqs.requested_by.user_id | reqs.create_uid

    def action_post(self):
        for rec in self:
            require_role(self.env, GROUP_RECEIVER, "Posting a goods receipt")
            if rec.state != "draft":
                raise UserError("Receipt %s is already %s." % (rec.name, rec.state))
            order = rec.purchase_order_id
            order._a06_assert_receivable()
            if not self.env.su and self.env.user in rec._a06_conflicted_receivers():
                raise UserError(
                    "Segregation of duties (SOD-02): you requested or bought PO %s and cannot "
                    "record its goods receipt." % order.name
                )
            lines = rec.line_ids.filtered(lambda ln: ln.qty_received > 0)
            if not lines:
                raise UserError("Receipt %s has no positive quantity." % rec.name)
            for line in lines:
                pol = line.po_line_id
                if pol.order_id != order:
                    raise UserError("Receipt %s mixes lines of another PO." % rec.name)
                already = pol.qty_received
                same = sum(
                    lines.filtered(lambda ln, p=pol: ln.po_line_id == p).mapped("qty_received")
                )
                ceiling = over_receipt_ceiling(self.env, pol.qty_ordered)
                if already + same > ceiling + 1e-6:
                    raise UserError(
                        "Received %.2f outside 0..%.2f for %s"
                        % (
                            already + same,
                            ceiling,
                            pol.description or pol.product_id.name or "?",
                        )
                    )
            required = bool_param(self.env, PARAM_INSPECTION, True)
            lines._guarded().write({"inspection_required": required})
            # A06 D5 / P13: the receipt's value in BDT is fixed now, at the
            # order's approved price and stamped rate; GRNI is cleared at it
            rate = order.sudo()._fix_rate_bdt()
            for line in lines:
                pol = line.po_line_id.sudo()
                price = pol.approved_unit_price if pol.approved_qty else pol.unit_price
                line._guarded().write({"unit_value_bdt": round((price or 0.0) * rate, 6)})
            rec._guarded().write(
                {
                    "state": "posted",
                    "received_on": fields.Date.context_today(rec),
                    "receiver_id": self.env.uid,
                    "posted_at": fields.Datetime.now(),
                }
            )
            # the receiver need not hold the buyer's write rights on the PO
            order.sudo()._a06_refresh_receipt_state()
            for line in lines:
                publish(
                    self.env,
                    "goods.received",
                    "fix.purchase.order.line",
                    line.po_line_id.id,
                    {
                        "po_ref": order.name,
                        "po_id": order.id,
                        "vendor_id": order.vendor_id.commercial_partner_id.id,
                        "product_id": line.product_id.id,
                        "qty_received": line.qty_received,
                        "receipt_ref": rec.name,
                        "received_on": str(rec.received_on),
                        # A06 P16: the vendor's own date, never a buyer-typed one
                        "promised_date": str(order._a06_otd_due_date())
                        if order._a06_otd_due_date()
                        else None,
                        "inspection_required": required,
                    },
                )
        return True

    def action_cancel(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(
                    "Only a draft receipt is cancelled (%s is %s)." % (rec.name, rec.state)
                )
            rec._guarded().write({"state": "cancelled"})
        return True


class FixPurchaseReceiptLine(models.Model):
    _name = "fix.purchase.receipt.line"
    _description = "Purchase Goods Receipt Line"
    _inherit = ["fix.guarded.mixin"]
    _order = "receipt_id, id"

    receipt_id = fields.Many2one(
        "fix.purchase.receipt", required=True, ondelete="cascade", index=True
    )
    po_line_id = fields.Many2one(
        "fix.purchase.order.line",
        string="PO Line",
        required=True,
        index=True,
        ondelete="restrict",
    )
    product_id = fields.Many2one(
        related="po_line_id.product_id", store=True, readonly=True, string="Product"
    )
    state = fields.Selection(related="receipt_id.state", store=True, readonly=True)
    qty_received = fields.Float(string="Received", required=True, default=0.0)
    unit_value_bdt = fields.Float(
        string="Receipt Unit Value (BDT)",
        digits=(16, 6),
        readonly=True,
        copy=False,
        help="The approved order price at the order's stamped exchange rate, fixed when the "
        "receipt is posted: what goods received not invoiced holds for one unit.",
    )
    inspection_required = fields.Boolean(readonly=True, copy=False, default=True)
    inspection_ids = fields.One2many(
        "fix.procurement.inspection", "receipt_line_id", string="Inspections"
    )
    qty_accepted = fields.Float(
        string="Accepted", compute="_compute_accepted", store=True, help="Matchable quantity."
    )
    qty_rejected = fields.Float(string="Rejected", compute="_compute_accepted", store=True)
    inspection_state = fields.Selection(
        [
            ("draft", "Not Posted"),
            ("not_required", "No Inspection Required"),
            ("pending", "Awaiting Inspection"),
            ("passed", "Passed"),
            ("partial", "Partially Accepted"),
            ("failed", "Failed"),
        ],
        compute="_compute_accepted",
        store=True,
    )

    _qty_positive = models.Constraint(
        "CHECK (qty_received > 0)", "A receipt line receives a positive quantity"
    )
    _rec_names_search = ["receipt_id.name", "product_id.name"]

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "inspection_required",
            "unit_value_bdt",
            "qty_accepted",
            "qty_rejected",
            "inspection_state",
        }

    @api.depends("receipt_id.name", "product_id.display_name", "qty_received")
    def _compute_display_name(self):
        # An inspection picker read "fix.purchase.receipt.line,7".
        for line in self:
            line.display_name = "%s · %s · %g" % (
                line.receipt_id.name or "",
                line.product_id.display_name or "",
                line.qty_received or 0.0,
            )

    @api.depends(
        "receipt_id.state",
        "qty_received",
        "inspection_required",
        "inspection_ids.state",
        "inspection_ids.qty_accepted",
    )
    def _compute_accepted(self):
        for line in self:
            done = line.inspection_ids.filtered(lambda i: i.state == "done")[:1]
            if line.receipt_id.state != "posted":
                accepted, status = 0.0, "draft"
            elif done:
                accepted = min(done.qty_accepted, line.qty_received)
                status = (
                    "passed"
                    if accepted >= line.qty_received - 1e-6
                    else ("failed" if accepted <= 1e-6 else "partial")
                )
            elif line.inspection_required:
                accepted, status = 0.0, "pending"
            else:
                accepted, status = line.qty_received, "not_required"
            line.qty_accepted = accepted
            line.inspection_state = status
            line.qty_rejected = (
                round(line.qty_received - accepted, 3)
                if status in ("passed", "partial", "failed")
                else 0.0
            )

    def _a06_check_open(self):
        if self._fix_guard_has_token():
            return
        if any(line.receipt_id.state != "draft" for line in self):
            raise UserError("A posted goods receipt is final; its lines cannot change.")

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._a06_check_open()
        for line in lines:
            if line.po_line_id.order_id != line.receipt_id.purchase_order_id:
                raise UserError("A receipt line must receive a line of the receipt's own PO.")
        return lines

    def write(self, vals):
        self._a06_check_open()
        return super().write(vals)

    def unlink(self):
        self._a06_check_open()
        return super().unlink()
