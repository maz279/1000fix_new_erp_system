# fix_procurement_ops — M16: RFQ sourcing events with bids and awards, blanket
# agreements, expediting, inspection outcomes, plus the requisition → PO
# conversion and the PO fields the OTD / cycle-time / maverick reports need.
# The module loads before cd_inventory, so references use product.product (the
# same basis as the existing PO lines), never fix.spare.part.
from odoo import api, fields, models
from odoo.exceptions import UserError


class FixRequisitionExtend(models.Model):
    _inherit = "fix.requisition"

    product_id = fields.Many2one("product.product", string="Product", index=True)
    qty = fields.Float(string="Quantity", default=1.0)
    vendor_id = fields.Many2one("res.partner", string="Preferred Vendor", index=True)

    def action_convert_to_po(self):
        """Create the PO from an approved requisition, one line at the
        requisition's estimated unit price. The PO keeps the requisition link
        so maverick spend (a PO with no approved requisition) is measurable."""
        orders = self.env["fix.purchase.order"]
        for req in self:
            if req.state != "approved":
                raise UserError("Convert an approved requisition")
            if not req.product_id or (req.qty or 0.0) <= 0:
                raise UserError("A requisition needs a product and a positive quantity to convert")
            if not req.vendor_id:
                raise UserError("A requisition needs a vendor before it can become a PO")
            if req.purchase_order_id:
                raise UserError("Requisition %s is already converted" % req.description)
            unit_price = (req.estimate_amount or 0.0) / (req.qty or 1.0)
            order = orders.create(
                {
                    "operating_unit_id": req.operating_unit_id.id,
                    "branch_id": req.branch_id.id,
                    "vendor_id": req.vendor_id.id,
                    "state": "draft",
                    "requisition_id": req.id,
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "product_id": req.product_id.id,
                                "description": req.description,
                                "qty_ordered": req.qty,
                                "unit_price": unit_price,
                            },
                        )
                    ],
                }
            )
            req.write({"state": "converted", "purchase_order_id": order.id})


class FixPurchaseOrderExtend(models.Model):
    _inherit = "fix.purchase.order"

    requisition_id = fields.Many2one("fix.requisition", string="Source Requisition", index=True)
    promised_date = fields.Date(string="Promised Date")
    received_on = fields.Date(string="Received On")

    def action_record_receipt(self, receipts=None):
        res = super().action_record_receipt(receipts or {})
        for order in self:
            if order.state == "received" and not order.received_on:
                order.received_on = fields.Date.context_today(self)
        return res


class FixProcurementRfq(models.Model):
    _name = "fix.procurement.rfq"
    _description = "RFQ Event"
    _order = "create_date desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    description = fields.Char(required=True)
    product_id = fields.Many2one("product.product", string="Product", required=True)
    qty = fields.Float(string="Quantity", default=1.0)
    required_by = fields.Date(string="Required By")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    target_price = fields.Monetary(string="Target Price", currency_field="currency_id")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("open", "Open for Bids"),
            ("closed", "Closed"),
            ("awarded", "Awarded"),
        ],
        required=True,
        default="draft",
    )
    bid_ids = fields.One2many("fix.procurement.bid", "rfq_id", string="Bids")
    notes = fields.Text()

    _qty_positive = models.Constraint("CHECK (qty > 0)", "RFQ quantity must be positive")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.procurement.rfq") or "RFQ/New"
                )
        return super().create(vals_list)

    def action_open(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Open a draft RFQ")
            rec.state = "open"

    def action_close(self):
        for rec in self:
            if rec.state != "open":
                raise UserError("Close an open RFQ")
            if not rec.bid_ids:
                raise UserError("An RFQ cannot close without at least one bid")
            rec.state = "closed"


class FixProcurementBid(models.Model):
    _name = "fix.procurement.bid"
    _description = "Supplier Bid"
    _order = "rfq_id, unit_price"

    name = fields.Char(required=True, default="New")
    rfq_id = fields.Many2one(
        "fix.procurement.rfq", string="RFQ", required=True, ondelete="cascade", index=True
    )
    vendor_id = fields.Many2one("res.partner", string="Vendor", required=True, ondelete="restrict")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    unit_price = fields.Monetary(string="Unit Price", currency_field="currency_id", required=True)
    lead_time_days = fields.Integer(string="Lead Time (days)", default=7)
    valid_until = fields.Date()
    state = fields.Selection(
        [("received", "Received"), ("awarded", "Awarded"), ("lost", "Lost")],
        required=True,
        default="received",
    )
    notes = fields.Char()

    _price_positive = models.Constraint("CHECK (unit_price > 0)", "Bid price must be positive")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.procurement.bid") or "BID/New"
                )
        return super().create(vals_list)


class FixProcurementAward(models.Model):
    """The award decision: created once per RFQ, marking the winning bid."""

    _name = "fix.procurement.award"
    _description = "Award Decision"
    _order = "decided_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    rfq_id = fields.Many2one(
        "fix.procurement.rfq", string="RFQ", required=True, ondelete="restrict", index=True
    )
    bid_id = fields.Many2one(
        "fix.procurement.bid", string="Winning Bid", required=True, ondelete="restrict"
    )
    decided_on = fields.Date(required=True, default=fields.Date.context_today)
    rationale = fields.Char()
    state = fields.Selection(
        [("decided", "Decided"), ("cancelled", "Cancelled")],
        required=True,
        default="decided",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.procurement.award") or "AWRD/New"
                )
        records = super().create(vals_list)
        for rec in records:
            if rec.bid_id.rfq_id != rec.rfq_id:
                raise UserError("The winning bid must belong to the awarded RFQ")
            rec.rfq_id.bid_ids.filtered(lambda b, won=rec.bid_id: b != won).write({"state": "lost"})
            rec.bid_id.write({"state": "awarded"})
            rec.rfq_id.state = "awarded"
        return records


class FixProcurementBlanket(models.Model):
    _name = "fix.procurement.blanket"
    _description = "Blanket Agreement"
    _order = "valid_to desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    vendor_id = fields.Many2one("res.partner", string="Vendor", required=True, ondelete="restrict")
    valid_from = fields.Date(required=True, default=fields.Date.context_today)
    valid_to = fields.Date(required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    cap_amount = fields.Monetary(string="Cap Amount", currency_field="currency_id")
    consumed_amount = fields.Monetary(
        string="Consumed (POs in window)",
        currency_field="currency_id",
        compute="_compute_consumed",
    )
    remaining_amount = fields.Monetary(
        string="Remaining", currency_field="currency_id", compute="_compute_consumed"
    )
    state = fields.Selection(
        [("active", "Active"), ("expired", "Expired"), ("cancelled", "Cancelled")],
        required=True,
        default="active",
    )

    _dates_ordered = models.Constraint(
        "CHECK (valid_to >= valid_from)", "The blanket end date cannot precede its start"
    )

    @api.depends("cap_amount", "vendor_id", "valid_from", "valid_to")
    def _compute_consumed(self):
        orders = self.env["fix.purchase.order"].sudo()
        for rec in self:
            domain = [("vendor_id", "=", rec.vendor_id.id), ("state", "!=", "cancelled")]
            if rec.valid_from:
                domain.append(("date_order", ">=", rec.valid_from))
            if rec.valid_to:
                domain.append(("date_order", "<=", rec.valid_to))
            consumed = sum(orders.search(domain).mapped("amount_total"))
            rec.consumed_amount = round(consumed, 2)
            rec.remaining_amount = round((rec.cap_amount or 0.0) - consumed, 2)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.procurement.blanket") or "BLKT/New"
                )
        return super().create(vals_list)


class FixProcurementExpedite(models.Model):
    _name = "fix.procurement.expedite"
    _description = "Expediting Case"
    _order = "create_date desc, id desc"

    name = fields.Char(required=True, default="New")
    purchase_order_id = fields.Many2one(
        "fix.purchase.order",
        string="Purchase Order",
        required=True,
        ondelete="cascade",
        index=True,
    )
    reason = fields.Char(required=True)
    promised_date = fields.Date()
    follow_up_date = fields.Date()
    state = fields.Selection(
        [("open", "Open"), ("chased", "Chased"), ("resolved", "Resolved")],
        required=True,
        default="open",
    )
    notes = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.procurement.expedite") or "EXPD/New"
                )
        return super().create(vals_list)

    def action_chase(self):
        for rec in self:
            if rec.state != "open":
                raise UserError("Chase an open case")
            rec.write({"state": "chased", "follow_up_date": fields.Date.context_today(self)})

    def action_resolve(self):
        for rec in self:
            if rec.state == "resolved":
                raise UserError("This case is already resolved")
            rec.state = "resolved"


class FixProcurementInspection(models.Model):
    """The inspection outcome of a delivery (the receipt itself is M15's)."""

    _name = "fix.procurement.inspection"
    _description = "Goods Inspection Outcome"
    _order = "inspected_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    receipt_ref = fields.Char(string="Receipt Reference", required=True)
    product_id = fields.Many2one("product.product", string="Product", required=True)
    qty_received = fields.Float(string="Received")
    qty_accepted = fields.Float(string="Accepted")
    qty_rejected = fields.Float(string="Rejected", compute="_compute_rejected", store=True)
    outcome = fields.Selection(
        [("accepted", "Accepted"), ("partial", "Partially Accepted"), ("rejected", "Rejected")],
        required=True,
        default="accepted",
    )
    inspected_on = fields.Date(required=True, default=fields.Date.context_today)
    inspector_id = fields.Many2one("hr.employee", string="Inspector")
    state = fields.Selection([("draft", "Draft"), ("done", "Done")], required=True, default="draft")
    notes = fields.Char()

    _qty_bounds = models.Constraint(
        "CHECK (qty_received >= 0 AND qty_accepted >= 0 AND qty_accepted <= qty_received)",
        "Accepted quantity must be between 0 and the received quantity",
    )

    @api.depends("qty_received", "qty_accepted")
    def _compute_rejected(self):
        for rec in self:
            rec.qty_rejected = round((rec.qty_received or 0.0) - (rec.qty_accepted or 0.0), 3)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.procurement.inspection") or "INSP/New"
                )
        return super().create(vals_list)

    def action_confirm(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Confirm a draft inspection")
            rec.state = "done"
