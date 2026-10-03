# fix.estimate — estimate and approval flow (P04-M03-T06).
# Customer-facing in Phase 5; built here per the roadmap.
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FixEstimate(models.Model):
    """A repair estimate — parts + labour + total, sent for customer approval."""
    _name = "fix.estimate"
    _description = "Repair Estimate"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "order_id, version desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    order_id = fields.Many2one("fix.service.order", string="Service Order",
                               required=True, ondelete="cascade", index=True)
    version = fields.Integer(default=1, required=True,
                             help="Incremented on each revision")

    state = fields.Selection(
        [("draft", "Draft"), ("sent", "Sent to Customer"),
         ("approved", "Approved"), ("rejected", "Rejected"),
         ("expired", "Expired")],
        default="draft", required=True, tracking=True)

    line_ids = fields.One2many("fix.estimate.line", "estimate_id", string="Lines")

    # BRU-SRM-07/08 approval evidence — documented customer approval above
    # BDT 5,000; customer + branch manager above BDT 25,000
    customer_approval_ref = fields.Char(
        string="Customer Approval Ref", copy=False,
        help="BRU-SRM-07: documented customer approval (SMS/OTP ref, signature id) "
             "— required above BDT 5,000 before work begins")
    manager_approval_uid = fields.Many2one(
        "res.users", string="Manager Approval", copy=False, readonly=True,
        help="BRU-SRM-08: branch-manager approval — required above BDT 25,000")
    APPROVAL_THRESHOLD = 5000       # customer approval documented
    DUAL_APPROVAL_THRESHOLD = 25000 # + branch manager

    # AS-10: Monetary totals
    parts_total = fields.Monetary(string="Parts Total", currency_field="currency_id",
                                  compute="_compute_totals", store=True)
    labour_total = fields.Monetary(string="Labour Total", currency_field="currency_id",
                                   compute="_compute_totals", store=True)
    discount = fields.Monetary(string="Discount", currency_field="currency_id", default=0.0)
    vat_rate = fields.Float(string="VAT Rate (%)", default=15.0,
                            help="Bangladesh standard VAT rate")
    vat_amount = fields.Monetary(string="VAT Amount", currency_field="currency_id",
                                 compute="_compute_totals", store=True)
    grand_total = fields.Monetary(string="Grand Total", currency_field="currency_id",
                                  compute="_compute_totals", store=True)
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))

    approved_by = fields.Many2one("res.partner", string="Approved By")
    approved_at = fields.Datetime(readonly=True)
    expiry_date = fields.Date(string="Estimate Valid Until")

    @api.depends("line_ids.line_total", "discount", "vat_rate")
    def _compute_totals(self):
        for est in self:
            est.parts_total = sum(est.line_ids.filtered(
                lambda l: l.line_type == "part").mapped("line_total"))
            est.labour_total = sum(est.line_ids.filtered(
                lambda l: l.line_type == "labour").mapped("line_total"))
            subtotal = est.parts_total + est.labour_total - est.discount
            est.vat_amount = subtotal * (est.vat_rate / 100.0)
            est.grand_total = subtotal + est.vat_amount

    def action_send(self):
        for est in self:
            est.state = "sent"
            est._emit_event("estimate.approved" if est.state == "approved" else "estimate.sent")

    def action_approve(self):
        """BRU-SRM-07 (H): above BDT 5,000 the CUSTOMER approval must be
        documented before the estimate can be approved; BRU-SRM-08 (H):
        above BDT 25,000 the BRANCH MANAGER approves too. Hard gates."""
        from odoo.exceptions import UserError
        for est in self:
            if est.grand_total > est.DUAL_APPROVAL_THRESHOLD:
                if not est.customer_approval_ref:
                    raise UserError(
                        "BRU-SRM-07: documented customer approval is required "
                        "before approving an estimate above BDT %.0f"
                        % est.DUAL_APPROVAL_THRESHOLD)
                if not est.manager_approval_uid:
                    raise UserError(
                        "BRU-SRM-08: branch-manager approval is required above "
                        "BDT %.0f (record the customer approval first, then have "
                        "the manager approve)"
                        % est.DUAL_APPROVAL_THRESHOLD)
            elif est.grand_total > est.APPROVAL_THRESHOLD and not est.customer_approval_ref:
                raise UserError(
                    "BRU-SRM-07: documented customer approval is required before "
                    "approving an estimate above BDT %.0f"
                    % est.APPROVAL_THRESHOLD)
            est.state = "approved"
            est.approved_at = fields.Datetime.now()
            est._emit_event("estimate.approved")

    def action_manager_approve(self):
        """The BRU-SRM-08 second key: the branch manager records their
        approval on an estimate already carrying customer approval."""
        from odoo.exceptions import UserError
        for est in self:
            if est.grand_total <= est.DUAL_APPROVAL_THRESHOLD:
                continue  # single approval suffices
            if not est.customer_approval_ref:
                raise UserError(
                    "BRU-SRM-08: customer approval must be documented before "
                    "the manager approves")
            est.manager_approval_uid = self.env.user

    def action_reject(self):
        for est in self:
            est.state = "rejected"
            est._emit_event("estimate.rejected")

    def action_revise(self):
        """Create a new version (T06: part-approval and revision)."""
        for est in self:
            new = est.copy({"version": est.version + 1, "state": "draft"})
            return {
                "type": "ir.actions.act_window",
                "res_model": "fix.estimate",
                "res_id": new.id,
                "view_mode": "form",
            }

    def _emit_event(self, event: str):
        from libs.py.fix_events import publish
        publish(self.env, event, "fix.estimate", self.id, {
            "estimate_id": self.id, "order_id": self.order_id.id,
            "version": self.version, "state": self.state,
            "grand_total": self.grand_total,
        })


class FixEstimateLine(models.Model):
    _name = "fix.estimate.line"
    _description = "Estimate Line"

    estimate_id = fields.Many2one("fix.estimate", required=True, ondelete="cascade")
    line_type = fields.Selection(
        [("part", "Part"), ("labour", "Labour"), ("diagnostic", "Diagnostic")],
        required=True, default="part")
    product_id = fields.Many2one("product.product", string="Product")
    description = fields.Char(required=True)
    quantity = fields.Float(default=1.0, digits="Product Unit of Measure")
    # AS-10: Monetary
    unit_price = fields.Monetary(string="Unit Price", currency_field="currency_id")
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    line_total = fields.Monetary(string="Line Total", currency_field="currency_id",
                                 compute="_compute_line_total", store=True)

    @api.depends("quantity", "unit_price")
    def _compute_line_total(self):
        for line in self:
            line.line_total = line.quantity * line.unit_price
