# cd_requisition — M16 Procurement core (P06-M07, CD-M16-01).
#
# The W3 slice: requisition -> PO (with ordered/received quantities that the
# M52 three-way match consumes), vendor events, and the P05 vendor-portal
# acknowledgement surface. RFQ sourcing events (CD-M16-03) land with the
# vendor portal completion.
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish  # FF-28


class FixPurchaseOrder(models.Model):
    """A purchase order: the ORDERED side of the three-way match."""

    _name = "fix.purchase.order"
    _description = "Purchase Order"
    # P03 workspace data-entry form (discovered by cd_p03_portal).
    _p03_capture = {
        "module": "M16",
        "form": "Purchase Order",
        "fields": ["vendor_id", "date_order", "branch_id"],
    }
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_order desc, id desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    branch_id = fields.Many2one("fix.branch", string="Deliver-to Branch", index=True)
    vendor_id = fields.Many2one("res.partner", string="Vendor", required=True,
                                index=True, ondelete="restrict")
    name = fields.Char(string="PO Reference", readonly=True, index=True, copy=False)
    date_order = fields.Datetime(string="Order Date", default=fields.Datetime.now,
                                 required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("sent", "Sent"), ("acknowledged", "Acknowledged"),
         ("partially_received", "Partially Received"), ("received", "Received"),
         ("closed", "Closed"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True)
    line_ids = fields.One2many("fix.purchase.order.line", "order_id", string="Lines")
    acknowledged_at = fields.Datetime(readonly=True,
                                      help="P05 vendor portal acknowledgement")
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    amount_total = fields.Monetary(string="Total", currency_field="currency_id",
                                   compute="_compute_total", store=True)

    @api.depends("line_ids.line_total")
    def _compute_total(self):
        for order in self:
            order.amount_total = sum(order.line_ids.mapped("line_total"))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "fix.purchase.order") or ("PO/%s" % fields.Date.today())
        return super().create(vals_list)

    def action_send(self):
        for order in self:
            order.state = "sent"
            publish(self.env, "po.issued", "fix.purchase.order", order.id, {
                "po_ref": order.name,
                "vendor_id": order.vendor_id.id,
                "amount_total": order.amount_total,
                "currency": order.currency_id.name,
            })

    def action_acknowledge(self, acknowledged_at=None):
        """P05 vendor portal calls this (PO acknowledgement, M09-T02)."""
        for order in self:
            if order.state != "sent":
                raise UserError("Only a sent PO can be acknowledged")
            order.write({"state": "acknowledged",
                         "acknowledged_at": acknowledged_at or fields.Datetime.now()})
            publish(self.env, "po.acknowledged", "fix.purchase.order", order.id, {
                "po_ref": order.name, "vendor_id": order.vendor_id.id})

    def action_record_receipt(self, receipts: dict[int, float]):
        """GRN intake: {line_id: qty_received_this_delivery}. Updates the
        RECEIVED side of the three-way match and publishes receipt events
        the M52 matcher consumes."""
        for order in self:
            for line in order.line_ids:
                add = receipts.get(line.id, 0.0)
                if add > 0:
                    line.qty_received += add
                    publish(self.env, "goods.received", "fix.purchase.order.line",
                            line.id, {
                                "po_ref": order.name,
                                "product_id": line.product_id.id,
                                "qty_received": add,
                            })
            fully = all(l.qty_received >= l.qty_ordered for l in order.line_ids)
            partly = any(l.qty_received > 0 for l in order.line_ids)
            order.state = ("received" if fully else
                           "partially_received" if partly else order.state)


class FixPurchaseOrderLine(models.Model):
    _name = "fix.purchase.order.line"
    _description = "Purchase Order Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    order_id = fields.Many2one("fix.purchase.order", required=True, ondelete="cascade")
    product_id = fields.Many2one("product.product", string="Product", required=True)
    description = fields.Char()
    currency_id = fields.Many2one(related="order_id.currency_id")
    qty_ordered = fields.Float(string="Ordered", required=True, default=1.0)
    qty_received = fields.Float(string="Received", default=0.0, copy=False)
    unit_price = fields.Monetary(string="Unit Price", currency_field="currency_id",
                                 required=True)
    line_total = fields.Monetary(string="Line Total", currency_field="currency_id",
                                 compute="_compute_line", store=True)

    @api.depends("qty_ordered", "unit_price")
    def _compute_line(self):
        for line in self:
            line.line_total = line.qty_ordered * line.unit_price

    @api.constrains("qty_ordered", "qty_received")
    def _check_quantities(self):
        for line in self:
            if line.qty_ordered <= 0:
                raise UserError("Ordered quantity must be positive")
            if line.qty_received < 0 or line.qty_received > line.qty_ordered:
                raise UserError(
                    "Received %.2f outside 0..%.2f for %s"
                    % (line.qty_received, line.qty_ordered, line.description or "?"))


class FixRequisition(models.Model):
    """An internal requisition that may mature into a PO (CD-M16-01)."""

    _name = "fix.requisition"
    _description = "Requisition"
    # P03 workspace data-entry form (discovered by cd_p03_portal).
    _p03_capture = {
        "module": "M16",
        "form": "Purchase Requisition",
        "fields": ["requested_by", "description", "urgency", "branch_id", "estimate_amount"],
    }
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    branch_id = fields.Many2one("fix.branch", string="Requesting Branch", index=True)
    requested_by = fields.Many2one("hr.employee", string="Requested By", required=True)
    description = fields.Char(required=True)
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    estimate_amount = fields.Monetary(string="Estimated Amount",
                                      currency_field="currency_id")
    urgency = fields.Selection(
        [("normal", "Normal"), ("urgent", "Urgent (stock-out)"),
         ("emergency", "Emergency (job-stopped)")],
        default="normal", required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("converted", "Converted to PO"),
         ("rejected", "Rejected")], default="draft", required=True, tracking=True)
    purchase_order_id = fields.Many2one("fix.purchase.order", string="Purchase Order",
                                        readonly=True, index=True)
    APPROVAL_THRESHOLD = 25000  # authority matrix (BRU-INV-11 companion)

    def action_approve(self):
        for req in self:
            if (req.estimate_amount > self.APPROVAL_THRESHOLD
                    and not self.env.user.has_group("base.group_system")):
                raise UserError(
                    "Requisitions above BDT %d require CFO-level approval"
                    % self.APPROVAL_THRESHOLD)
            req.state = "approved"
