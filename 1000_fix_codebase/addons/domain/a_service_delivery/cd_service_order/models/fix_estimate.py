# fix.estimate — estimate and approval flow (P04-M03-T06).
# Customer-facing in Phase 5; built here per the roadmap.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class FixEstimate(models.Model):
    """A repair estimate — parts + labour + total, sent for customer approval."""

    _name = "fix.estimate"
    _description = "Repair Estimate"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "order_id, version desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    order_id = fields.Many2one(
        "fix.service.order", string="Service Order", required=True, ondelete="cascade", index=True
    )
    version = fields.Integer(default=1, required=True, help="Incremented on each revision")

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("sent", "Sent to Customer"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("expired", "Expired"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )

    # copy=True: a revision (action_revise) carries the lines - One2many fields
    # are not copied by default, so every revision used to be an EMPTY estimate.
    line_ids = fields.One2many("fix.estimate.line", "estimate_id", string="Lines", copy=True)

    # BRU-SRM-07/08 approval evidence — documented customer approval above
    # BDT 5,000; customer + branch manager above BDT 25,000
    customer_approval_ref = fields.Char(
        string="Customer Approval Ref",
        copy=False,
        help="BRU-SRM-07: documented customer approval (SMS/OTP ref, signature id) "
        "— required above BDT 5,000 before work begins",
    )
    manager_approval_uid = fields.Many2one(
        "res.users",
        string="Manager Approval",
        copy=False,
        readonly=True,
        help="BRU-SRM-08: branch-manager approval — required above BDT 25,000",
    )
    APPROVAL_THRESHOLD = 5000  # BRU-SRM-07 default; config-param overridable
    DUAL_APPROVAL_THRESHOLD = 25000  # BRU-SRM-08 default; config-param overridable

    @api.model
    def _threshold_customer(self) -> float:
        """BRU-SRM-07 customer-approval threshold (BDT) — overridable via the
        ``cd_service_order.estimate_threshold_customer`` config parameter so
        the Approval Thresholds screen reflects one live value."""
        return float(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("cd_service_order.estimate_threshold_customer", self.APPROVAL_THRESHOLD)
        )

    @api.model
    def _threshold_dual(self) -> float:
        """BRU-SRM-08 dual-approval threshold (BDT) — overridable via
        ``cd_service_order.estimate_threshold_dual``."""
        return float(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("cd_service_order.estimate_threshold_dual", self.DUAL_APPROVAL_THRESHOLD)
        )

    # AS-10: Monetary totals
    parts_total = fields.Monetary(
        string="Parts Total", currency_field="currency_id", compute="_compute_totals", store=True
    )
    labour_total = fields.Monetary(
        string="Labour Total", currency_field="currency_id", compute="_compute_totals", store=True
    )
    # The diagnostic fee is a priced estimate line (RF-009 sample estimate line 3,
    # FR-SRM-029 / BRU-QTE-12): it was summed into NO total, so a charged
    # diagnostic fee never reached the subtotal, the VAT base or the grand total.
    diagnostic_total = fields.Monetary(
        string="Diagnostic Total",
        currency_field="currency_id",
        compute="_compute_totals",
        store=True,
    )
    discount = fields.Monetary(string="Discount", currency_field="currency_id", default=0.0)
    vat_rate = fields.Float(
        string="VAT Rate (%)", default=15.0, help="Bangladesh standard VAT rate"
    )
    vat_amount = fields.Monetary(
        string="VAT Amount", currency_field="currency_id", compute="_compute_totals", store=True
    )
    grand_total = fields.Monetary(
        string="Grand Total", currency_field="currency_id", compute="_compute_totals", store=True
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )

    approved_by = fields.Many2one("res.partner", string="Approved By")
    approved_at = fields.Datetime(readonly=True, copy=False)
    expiry_date = fields.Date(string="Estimate Valid Until")

    # line_type is a dependency: re-typing a line moves it between the totals
    # (it was missing, so a re-typed line kept its old bucket until another change).
    @api.depends("line_ids.line_total", "line_ids.line_type", "discount", "vat_rate")
    def _compute_totals(self):
        for est in self:
            totals = {"part": 0.0, "labour": 0.0, "diagnostic": 0.0}
            for line in est.line_ids:
                totals[line.line_type] += line.line_total
            est.parts_total = totals["part"]
            est.labour_total = totals["labour"]
            est.diagnostic_total = totals["diagnostic"]
            subtotal = est._chargeable_total() - est.discount
            est.vat_amount = subtotal * (est.vat_rate / 100.0)
            est.grand_total = subtotal + est.vat_amount

    def _chargeable_total(self) -> float:
        """Parts + labour + diagnostic: the VAT-exclusive amount before discount."""
        self.ensure_one()
        return self.parts_total + self.labour_total + self.diagnostic_total

    @api.constrains("discount", "line_ids")
    def _check_discount(self):
        """A discount is never negative and never exceeds the parts + labour +
        diagnostic amount it discounts - otherwise the subtotal goes negative, VAT
        is charged on a negative base and a negative "revenue" reaches the Role
        Centre (R01 re-audit 2026-10-22: estimate with no lines, discount 200 ->
        grand total -200.30)."""
        for est in self:
            if est.discount < 0:
                raise ValidationError("An estimate discount cannot be negative.")
            chargeable = est._chargeable_total()
            if est.discount > chargeable:
                raise ValidationError(
                    "The discount (%.2f) cannot exceed the parts, labour and diagnostic "
                    "total (%.2f)." % (est.discount, chargeable)
                )

    def _check_has_lines(self, action: str) -> None:
        for est in self:
            if not est.line_ids:
                raise UserError(
                    "An estimate with no parts, labour or diagnostic lines cannot be %s." % action
                )

    def action_send(self):
        self._check_has_lines("sent to the customer")
        for est in self:
            est.state = "sent"
            est._emit_event("estimate.sent")

    def action_approve(self):
        """BRU-SRM-07 (H): above the customer threshold the CUSTOMER approval
        must be documented before the estimate can be approved; BRU-SRM-08
        (H): above the dual threshold the BRANCH MANAGER approves too. Hard
        gates. Thresholds default to BDT 5,000 / 25,000 and are config-param
        overridable — the live values drive the Approval Thresholds screen."""
        self._check_has_lines("approved")
        customer_threshold = self._threshold_customer()
        dual_threshold = self._threshold_dual()
        for est in self:
            if est.grand_total > dual_threshold:
                if not est.customer_approval_ref:
                    raise UserError(
                        "BRU-SRM-07: documented customer approval is required "
                        "before approving an estimate above BDT %.0f" % dual_threshold
                    )
                if not est.manager_approval_uid:
                    raise UserError(
                        "BRU-SRM-08: branch-manager approval is required above "
                        "BDT %.0f (record the customer approval first, then have "
                        "the manager approve)" % dual_threshold
                    )
            elif est.grand_total > customer_threshold and not est.customer_approval_ref:
                raise UserError(
                    "BRU-SRM-07: documented customer approval is required before "
                    "approving an estimate above BDT %.0f" % customer_threshold
                )
            est.state = "approved"
            est.approved_at = fields.Datetime.now()
            est._emit_event("estimate.approved")

    def action_manager_approve(self):
        """The BRU-SRM-08 second key: the branch manager records their
        approval on an estimate already carrying customer approval."""
        dual_threshold = self._threshold_dual()
        for est in self:
            if est.grand_total <= dual_threshold:
                continue  # single approval suffices
            if not est.customer_approval_ref:
                raise UserError(
                    "BRU-SRM-08: customer approval must be documented before "
                    "the manager approves"
                )
            est.manager_approval_uid = self.env.user

    def action_reject(self):
        for est in self:
            est.state = "rejected"
            est._emit_event("estimate.rejected")

    def action_revise(self):
        """Create a new version (T06: part-approval and revision), lines included."""
        self.ensure_one()
        new = self.copy({"version": self.version + 1, "state": "draft"})
        return {
            "type": "ir.actions.act_window",
            "res_model": "fix.estimate",
            "res_id": new.id,
            "view_mode": "form",
        }

    def _emit_event(self, event: str):
        from libs.py.fix_events import publish

        publish(
            self.env,
            event,
            "fix.estimate",
            self.id,
            {
                "estimate_id": self.id,
                "order_id": self.order_id.id,
                "version": self.version,
                "state": self.state,
                "grand_total": self.grand_total,
            },
        )


class FixEstimateLine(models.Model):
    _name = "fix.estimate.line"
    _description = "Estimate Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    estimate_id = fields.Many2one("fix.estimate", required=True, ondelete="cascade")
    line_type = fields.Selection(
        [("part", "Part"), ("labour", "Labour"), ("diagnostic", "Diagnostic")],
        required=True,
        default="part",
    )
    product_id = fields.Many2one("product.product", string="Product")
    description = fields.Char(required=True)
    quantity = fields.Float(default=1.0, digits="Product Unit of Measure")
    # AS-10: Monetary
    unit_price = fields.Monetary(string="Unit Price", currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    line_total = fields.Monetary(
        string="Line Total", currency_field="currency_id", compute="_compute_line_total", store=True
    )

    @api.depends("quantity", "unit_price")
    def _compute_line_total(self):
        for line in self:
            line.line_total = line.quantity * line.unit_price

    # The estimate-level _check_discount only runs when the ESTIMATE is written;
    # a line priced down, re-typed or deleted directly lowered parts + labour
    # under the discount unchecked (negative subtotal, negative VAT).
    @api.constrains("quantity", "unit_price", "line_type", "estimate_id")
    def _check_estimate_discount(self):
        self.estimate_id._check_discount()

    def unlink(self):
        estimates = self.estimate_id
        result = super().unlink()
        estimates.exists()._check_discount()
        return result
