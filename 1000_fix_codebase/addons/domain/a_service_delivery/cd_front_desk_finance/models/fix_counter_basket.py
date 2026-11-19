# Quote-to-cash P2 (13 Nov 2026): the counter sells more than one item at a
# time, and takes every payment method on the one M20 list.
#
# A counter sale (fix.counter.sale, cd_front_desk) is one product; its
# posting (VAT, GL, stock, in this module) is proven per sale. A basket is
# the customer's whole purchase: its lines, one payment, one receipt. On
# confirm it raises one counter sale per line through the counter sale's own
# confirm, so every line is posted, priced and approved exactly as a single
# sale is; a refusal on any line confirms none (one savepoint).
#
# Counter sales also take Rocket and Upay (both MFS: the same two-stage MFS
# clearing as bKash / Nagad), and record the M20 payment method they were
# paid by.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

# fix.payment.method code -> fix.counter.sale.payment_method
COUNTER_METHOD = {
    "CASH": "cash",
    "BKASH": "bkash",
    "NAGAD": "nagad",
    "ROCKET": "rocket",
    "UPAY": "upay",
    "CARD": "card",
    "SSLCZ": "card",
}


class FixCounterSaleMethod(models.Model):
    _inherit = "fix.counter.sale"

    payment_method = fields.Selection(
        selection_add=[("rocket", "Rocket"), ("upay", "Upay")],
        ondelete={"rocket": "set default", "upay": "set default"},
    )
    payment_method_id = fields.Many2one(
        "fix.payment.method",
        string="Paid By",
        domain="[('for_counter', '=', True)]",
        help="The M20 payment method; sets the counter's tender.",
    )
    basket_id = fields.Many2one("fix.counter.basket", readonly=True, index=True, copy=False)

    @api.model
    def _counter_method_for(self, method):
        if not method:
            return None
        key = COUNTER_METHOD.get(method.code or "")
        if not key or not method.for_counter:
            raise UserError("%s is not taken at the counter." % method.name)
        return key

    @api.model_create_multi
    def create(self, vals_list):
        Method = self.env["fix.payment.method"]
        for vals in vals_list:
            method = Method.browse(vals.get("payment_method_id")).exists()
            if method:
                vals["payment_method"] = self._counter_method_for(method)
        return super().create(vals_list)

    def write(self, vals):
        if vals.get("payment_method_id"):
            method = self.env["fix.payment.method"].browse(vals["payment_method_id"]).exists()
            vals = dict(vals, payment_method=self._counter_method_for(method))
        return super().write(vals)


class FixCounterBasket(models.Model):
    _name = "fix.counter.basket"
    _description = "Counter Basket (multi-item counter sale)"
    _inherit = ["mail.thread"]
    _order = "id desc"

    name = fields.Char(default="New", readonly=True, copy=False, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    branch_id = fields.Many2one("fix.branch", string="Branch", index=True)
    customer_id = fields.Many2one("res.partner", string="Customer")
    payment_method_id = fields.Many2one(
        "fix.payment.method",
        string="Paid By",
        required=True,
        domain="[('for_counter', '=', True)]",
    )
    transaction_ref = fields.Char(string="TrxID / Card Slip")
    tendered_amount = fields.Float(string="Cash Tendered (BDT)")
    line_ids = fields.One2many("fix.counter.basket.line", "basket_id", string="Items", copy=True)
    total = fields.Float(string="Total (BDT)", compute="_compute_total", store=True)
    change_due = fields.Float(string="Change Due (BDT)", compute="_compute_total", store=True)
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed")],
        default="draft",
        required=True,
        readonly=True,
        tracking=True,
    )
    sale_ids = fields.One2many("fix.counter.sale", "basket_id", string="Counter Sales")

    @api.depends("line_ids.subtotal", "tendered_amount", "payment_method_id")
    def _compute_total(self):
        for rec in self:
            rec.total = round(sum(rec.line_ids.mapped("subtotal")), 2)
            cash = rec.payment_method_id.code == "CASH"
            rec.change_due = (
                round(max((rec.tendered_amount or 0.0) - rec.total, 0.0), 2) if cash else 0.0
            )

    @api.model_create_multi
    def create(self, vals_list):
        Sale = self.env["fix.counter.sale"]
        for vals in vals_list:
            vals.pop("state", None)
            # the workspace form never asks: the unit is the branch's, as on a
            # single counter sale
            if not vals.get("operating_unit_id"):
                vals["operating_unit_id"] = Sale._fd_default_operating_unit(vals)
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.counter.basket") or "New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if "state" in vals and not self.env.su:
            raise UserError("A basket is confirmed by its action only.")
        if set(vals) - {"state"} and any(b.state != "draft" for b in self):
            raise UserError("A confirmed basket is final; refund its sales instead.")
        return super().write(vals)

    def _fdf_drop_draft_sales(self):
        """A changed basket drops the draft sales drafted from its old lines
        (and their price requests): a stale price is never confirmed."""
        drafts = self.sudo().sale_ids.filtered(lambda s: s.state == "draft")
        if drafts:
            drafts.unlink()

    def action_confirm(self):
        """One counter sale per line, confirmed by the counter sale's own
        rules (cashier, price approval, TrxID, open cash shift)."""
        Sale = self.env["fix.counter.sale"]
        for rec in self:
            if rec.state != "draft":
                raise UserError("Basket %s is already confirmed." % rec.name)
            if not rec.line_ids:
                raise UserError("Basket %s has no items." % rec.name)
            method = rec.payment_method_id
            key = Sale._counter_method_for(method)
            if key != "cash" and not (rec.transaction_ref or "").strip():
                raise UserError(
                    "Basket %s is paid by %s: enter its TrxID or card slip number."
                    % (rec.name, method.name)
                )
            if key == "cash" and rec.tendered_amount and rec.tendered_amount + 0.005 < rec.total:
                raise UserError(
                    "Basket %s: BDT %.2f tendered does not cover the BDT %.2f total."
                    % (rec.name, rec.tendered_amount, rec.total)
                )
            # A02 ERP audit M04-F6: a basket with a below-list line could never
            # confirm (the price approval was requested on a sale that rolled
            # back with the refusal). Its sales are drafted once and kept; every
            # price approval is requested before anything confirms; the basket
            # confirms once all are approved.
            sales = rec.sale_ids.filtered(lambda s: s.state == "draft")
            if not sales:
                sales = Sale.create(
                    [
                        {
                            "company_id": rec.company_id.id,
                            "operating_unit_id": rec.operating_unit_id.id,
                            "branch_id": rec.branch_id.id or False,
                            "customer_id": rec.customer_id.id or False,
                            "product_id": line.product_id.id,
                            "quantity": line.quantity,
                            "unit_price": line.unit_price,
                            "payment_method_id": method.id,
                            "transaction_ref": rec.transaction_ref or False,
                            # each sale is fully paid from the basket's tender
                            "tendered_amount": round(line.subtotal, 2) if key == "cash" else 0.0,
                            "basket_id": rec.id,
                        }
                        for line in rec.line_ids
                    ]
                )
            if hasattr(sales, "_fd_price_blocked") and sales._fd_price_blocked():
                waiting = sales.action_request_price_approvals()
                rec.message_post(
                    body="Awaiting price approval for %s; the basket confirms once every "
                    "below-list price is approved." % ", ".join(waiting.mapped("name"))
                )
                continue
            with self.env.cr.savepoint():
                sales.action_confirm()
            rec.sudo().write({"state": "confirmed"})
            rec.message_post(
                body="Confirmed as %s (BDT %.2f by %s)."
                % (", ".join(sales.mapped("name")), rec.total, method.name)
            )
        return True


class FixCounterBasketLine(models.Model):
    _name = "fix.counter.basket.line"
    _description = "Counter Basket Item"
    _order = "basket_id, sequence, id"

    basket_id = fields.Many2one("fix.counter.basket", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="basket_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="basket_id.operating_unit_id", store=True, index=True
    )
    sequence = fields.Integer(default=10)
    product_id = fields.Many2one("product.product", string="Item", required=True)
    quantity = fields.Float(default=1.0, required=True)
    unit_price = fields.Float(string="Unit Price (BDT)")
    subtotal = fields.Float(string="Amount (BDT)", compute="_compute_subtotal", store=True)

    @api.depends("quantity", "unit_price")
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = round((line.quantity or 0.0) * (line.unit_price or 0.0), 2)

    @api.model_create_multi
    def create(self, vals_list):
        Product = self.env["product.product"]
        for vals in vals_list:
            # an empty price (the workspace grid sends 0) is the list price
            if not vals.get("unit_price"):
                vals["unit_price"] = Product.browse(vals.get("product_id")).lst_price
        lines = super().create(vals_list)
        if lines.basket_id.filtered(lambda b: b.state != "draft"):
            raise UserError("A confirmed basket is final.")
        lines.basket_id._fdf_drop_draft_sales()
        return lines

    @api.constrains("quantity", "unit_price")
    def _check_numbers(self):
        for line in self:
            if (line.quantity or 0.0) <= 0 or (line.unit_price or 0.0) < 0:
                raise ValidationError(
                    "A basket item has a positive quantity and no negative price."
                )

    def write(self, vals):
        if any(line.basket_id.state != "draft" for line in self):
            raise UserError("A confirmed basket is final.")
        self.basket_id._fdf_drop_draft_sales()
        return super().write(vals)

    def unlink(self):
        if any(line.basket_id.state != "draft" for line in self):
            raise UserError("A confirmed basket is final.")
        self.basket_id._fdf_drop_draft_sales()
        return super().unlink()
