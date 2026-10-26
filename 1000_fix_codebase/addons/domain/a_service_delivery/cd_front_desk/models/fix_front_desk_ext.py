# M04 extensions (P04-M02 follow-up): state guards the queue never had, the
# dead states made reachable, the token→order link actually written, and the
# counter-sales model the module always named but never had.
from odoo import api, fields, models
from odoo.exceptions import UserError


class FixTokenQueueExt(models.Model):
    _inherit = "fix.token.queue"

    def action_call(self):
        for token in self:
            if token.state not in ("waiting", "no_show"):
                raise UserError(
                    "Token %s cannot be called from state '%s'."
                    % (token.token_display, token.state)
                )
        return super().action_call()

    def action_serving(self):
        for token in self:
            if token.state != "called":
                raise UserError(
                    "Token %s must be called before serving (current: %s)."
                    % (token.token_display, token.state)
                )
        return super().action_serving()

    def action_complete(self):
        for token in self:
            if token.state != "serving":
                raise UserError(
                    "Token %s must be serving before completion (current: %s)."
                    % (token.token_display, token.state)
                )
        return super().action_complete()

    def action_no_show(self):
        """Mark a called token as no-show (it can be re-called later)."""
        for token in self:
            if token.state not in ("waiting", "called"):
                raise UserError(
                    "Only waiting or called tokens can be marked no-show (current: %s)."
                    % token.state
                )
            token.state = "no_show"

    def action_cancel(self):
        for token in self:
            if token.state == "completed":
                raise UserError("Completed token %s cannot be cancelled." % token.token_display)
            token.state = "cancelled"


class FixWalkinIntakeExt(models.Model):
    _inherit = "fix.walkin.intake"

    def action_submit_for_handover(self):
        """The handover_pending state existed in the Selection but no code
        ever set it — intake jumped straight to completed. Submitting parks
        the device at the counter awaiting the customer's acknowledgement."""
        for intake in self:
            if intake.state != "in_progress":
                raise UserError(
                    "Only in-progress intakes can be submitted for handover (current: %s)."
                    % intake.state
                )
            intake.state = "handover_pending"

    def action_complete_handover(self):
        for intake in self:
            if intake.state not in ("in_progress", "handover_pending"):
                raise UserError(
                    "Intake %s cannot complete handover from state '%s'."
                    % (intake.display_name or intake.id, intake.state)
                )
        orders = super().action_complete_handover()
        # the token↔order link existed as a field nobody ever wrote
        for intake in self:
            if intake.token_id and intake.service_order_id:
                intake.token_id.service_order_id = intake.service_order_id
        return orders


class FixCashShiftExt(models.Model):
    _inherit = "fix.cash.shift"

    def action_confirm_closed(self):
        """The 'closed' state existed but was unreachable — reconcile jumped
        counting → reconciled/discrepancy. Confirming the count closes the
        shift (variance frozen); reconcile then stamps the outcome. A 0.00
        count is a legitimate empty drawer (the model's own convention)."""
        for shift in self:
            if shift.state != "counting":
                raise UserError(
                    "Only shifts in counting can be confirmed closed (current: %s)." % shift.state
                )
            shift.state = "closed"
            shift.closed_at = fields.Datetime.now()

    def action_reconcile(self):
        for shift in self:
            if shift.state == "closed":
                # reopening the reconciliation path from the (previously
                # dead) closed state
                shift.state = "counting"
        return super().action_reconcile()


class FixCounterSale(models.Model):
    """A counter sale — parts, accessories and protection plans sold over
    the branch counter (walk-in, no service order). The module's registry
    always listed Counter Sales; the model never existed. Money fields are
    BDT per AS-10; the shift link puts the sale in the drawer's takings."""

    _name = "fix.counter.sale"
    _description = "Counter Sale"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    name = fields.Char(string="Sale No.", readonly=True, index=True, copy=False)
    shift_id = fields.Many2one(
        "fix.cash.shift", string="Cash Shift", index=True, ondelete="set null"
    )
    branch_id = fields.Many2one("fix.branch", string="Branch", index=True)
    customer_id = fields.Many2one("res.partner", string="Customer")
    product_id = fields.Many2one("product.product", string="Product", required=True, index=True)
    quantity = fields.Float(default=1.0, required=True)
    unit_price = fields.Float(
        string="Unit Price (BDT)",
        required=True,
        help="Counter price in BDT — defaults from the product's sale price.",
    )
    total = fields.Float(string="Total (BDT)", compute="_compute_total", store=True)
    payment_method = fields.Selection(
        [
            ("cash", "Cash"),
            ("bkash", "bKash"),
            ("nagad", "Nagad"),
            ("card", "Card"),
        ],
        default="cash",
        required=True,
    )
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed"), ("refunded", "Refunded")],
        default="draft",
        required=True,
        tracking=True,
    )
    sale_date = fields.Datetime(default=fields.Datetime.now, required=True)
    sold_by = fields.Many2one("hr.employee", string="Sold By")

    @api.depends("quantity", "unit_price")
    def _compute_total(self):
        for sale in self:
            sale.total = round(sale.quantity * sale.unit_price, 2)

    @api.onchange("product_id")
    def _onchange_product_id(self):
        if self.product_id and not self.unit_price:
            self.unit_price = self.product_id.list_price or 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name"):
                seq = self.env["ir.sequence"].next_by_code("fix.counter.sale")
                vals["name"] = seq or "CS/%s" % fields.Date.today()
        return super().create(vals_list)

    def action_confirm(self):
        for sale in self:
            if sale.state != "draft":
                raise UserError("Only draft counter sales can be confirmed.")
            sale.state = "confirmed"
            # cash sales join the drawer's expected takings for their shift
            if sale.payment_method == "cash" and sale.shift_id:
                sale.shift_id.cash_payments = sale.shift_id.cash_payments + sale.total

    def action_refund(self):
        for sale in self:
            if sale.state != "confirmed":
                raise UserError("Only confirmed sales can be refunded.")
            sale.state = "refunded"
            if sale.payment_method == "cash" and sale.shift_id:
                sale.shift_id.cash_refunds = sale.shift_id.cash_refunds + sale.total
