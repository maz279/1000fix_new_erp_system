# A service order's money and its invoice (A02 ERP audit, 19 Nov 2026).
#
# 1. The receipts that paid an order. M01 releases no device unpaid: the money
#    is recorded on the order (_fix_record_settlement) before delivery, but the
#    M20 invoice joined none of it, so the order's invoice stayed open on AR
#    (aged, dunned, credit-held) for a customer who had paid, while the
#    receipt sat unapplied. A receipt now names the order it paid
#    (source_order_id) and the invoice applies every such receipt the moment
#    it is issued (fix.ar.invoice._fix_apply_order_settlement).
#
# 2. The tax point. The invoice (Mushak 6.3, revenue, output VAT) was raised
#    only when somebody pressed Close, which nothing forces: a delivered,
#    paid order could carry no tax invoice for weeks and its VAT fall into a
#    later return. The supply is the delivery (BRU-SRM-05 allows Delivered),
#    so the invoice is raised at delivery; the hourly service_order.closed
#    drain stays as the safety net (idempotent on the order).
import logging
from decimal import ROUND_HALF_UP, Decimal

from odoo import api, fields, models
from odoo.addons.cd_tax_engine_bd.models import tax_logic
from odoo.exceptions import AccessError, UserError, ValidationError

from .fix_billing_engine import TWO_PLACES, allocate_discount, dhaka_date, m51_determine
from .fix_finance_approval import GROUP_ADMINISTRATOR, has_role

_logger = logging.getLogger(__name__)


class FixArReceiptOrderLink(models.Model):
    _inherit = "fix.ar.receipt"

    source_order_id = fields.Many2one(
        "fix.service.order",
        string="Service Order Paid",
        readonly=True,
        copy=False,
        index=True,
        help="The service order this money paid (counter, field or M20 receipt settlement, "
        "or an advance such as the diagnostic fee). The order's invoice applies it.",
    )

    is_order_advance = fields.Boolean(
        string="Advance on the Order",
        readonly=True,
        copy=False,
        help="Money taken before the price was settled (e.g. the walk-in diagnostic fee). "
        "It reduces what the order still owes and is applied to the order's invoice.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"source_order_id", "is_order_advance"}


class FixServiceOrderSettlementReceipts(models.Model):
    _inherit = "fix.service.order"

    credit_released_by = fields.Many2one(
        "res.users", string="Released on Credit By", readonly=True, copy=False
    )
    credit_released_at = fields.Datetime(string="Released on Credit At", readonly=True, copy=False)
    # A02 pass 2 (M01-04): the amount the release covers. The gates and the
    # customer's exposure honour the credit only up to it; a higher amount
    # due voids the release (released again on the new amount).
    credit_released_amount = fields.Monetary(
        string="Released on Credit (BDT)",
        currency_field="currency_id",
        readonly=True,
        copy=False,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "credit_released_by",
            "credit_released_at",
            "credit_released_amount",
        }

    # ------------------------------------------------- B2B credit (X-08 / M01-F6)
    def action_release_on_credit(self):
        """A corporate customer takes the device on account: the delivery and
        close gates honoured 'credit_approved', but nothing could set it, so a
        credit customer had to pay at the counter (or staff faked a counter
        settlement). A Finance Manager releases it against the customer's M33
        credit profile: a credit limit, no hold, and room under the limit for
        the amount due. Never the person who raised the order."""
        if not has_role(self.env, GROUP_ADMINISTRATOR):
            raise UserError("Only a Finance Manager releases an order on credit.")
        Profile = self.env["fix.credit.profile"].sudo()
        for order in self:
            if order.payment_settlement_state != "unpaid":
                raise UserError(
                    "Order %s is %s: only an unpaid order is released on credit."
                    % (order.name, order.payment_settlement_state)
                )
            if order.state in ("closed", "cancelled", "delivered"):
                raise UserError("Order %s is %s." % (order.name, order.state))
            if not self.env.su and self.env.user == order.create_uid:
                raise UserError(
                    "Segregation of duties: the person who raised order %s cannot release it "
                    "on credit." % order.name
                )
            due = order._fix_amount_due()
            if due <= 0.005:
                raise UserError("Order %s owes nothing: there is no credit to give." % order.name)
            customer = order.customer_id.commercial_partner_id
            company = order.company_id or self.env.company
            profile = Profile.search(
                [("customer_id", "=", customer.id), ("company_id", "=", company.id)], limit=1
            )
            if not profile or profile.credit_limit <= 0:
                raise UserError(
                    "%s has no credit limit in M33: the order is paid before release."
                    % customer.display_name
                )
            if profile.credit_hold:
                raise UserError(
                    "%s is on credit hold (%s)."
                    % (customer.display_name, profile.hold_reason or "no reason recorded")
                )
            exposure = order._fix_live_credit_exposure(customer, company)
            room = round(profile.credit_limit - exposure, 2)
            if due > room + 0.005:
                raise UserError(
                    "Order %s owes BDT %.2f; %s has BDT %.2f left under its BDT %.2f limit."
                    % (order.name, due, customer.display_name, room, profile.credit_limit)
                )
            order._guarded().write(
                {
                    "payment_settlement_state": "credit_approved",
                    "credit_released_by": self.env.user.id,
                    "credit_released_at": fields.Datetime.now(),
                    "credit_released_amount": due,
                }
            )
            order.message_post(
                body="Released on credit by %s: BDT %.2f on account (limit BDT %.2f, exposure "
                "BDT %.2f). The tax invoice is raised at delivery and collected on terms."
                % (self.env.user.name, due, profile.credit_limit, exposure)
            )
        return True

    def _fix_live_credit_exposure(self, customer, company) -> float:
        """What the customer owes on account right now, read at the moment of
        release (the profile's stored exposure is recomputed only when its
        limit or customer changes, so it went stale; and it counted neither
        invoices raised on the customer's contact persons nor orders already
        released on credit that are not invoiced yet, so a Finance Manager
        could release order after order against the same room):
          open residuals of issued invoices of the commercial partner and its
          contacts in the company
        + the amount due of the customer's OTHER orders released on credit
          that carry no invoice yet."""
        self.ensure_one()
        Invoice = self.env["fix.ar.invoice"].sudo()
        invoices = Invoice.search(
            [
                ("customer_id", "child_of", customer.id),
                ("state", "=", "issued"),
                ("company_id", "=", company.id),
            ]
        )
        exposure = sum(invoices.mapped("amount_residual"))
        others = self.sudo().search(
            [
                ("id", "!=", self.id),
                ("customer_id", "child_of", customer.id),
                ("company_id", "=", company.id),
                ("payment_settlement_state", "=", "credit_approved"),
                ("state", "not in", ("cancelled",)),
            ]
        )
        if others:
            invoiced = set(
                Invoice.search(
                    [
                        ("source_model", "=", "fix.service.order"),
                        ("source_id", "in", others.ids),
                        ("state", "!=", "cancelled"),
                    ]
                ).mapped("source_id")
            )
            # M01-04: an order released on credit commits what was released
            # (or more, if its price has since risen and the release is void)
            exposure += sum(
                max(o._fix_amount_due(), o.credit_released_amount or 0.0)
                for o in others
                if o.id not in invoiced
            )
        return round(exposure, 2)

    def _fix_check_credit_release(self) -> None:
        """M01-04: a release covers the amount it was given for. When the
        amount due rises above it (a revised estimate approved), the release
        is void and the order is unpaid again until a Finance Manager
        releases it on the new amount, or it is paid."""
        for order in self.sudo().filtered(
            lambda o: o.payment_settlement_state == "credit_approved"
            and o.state not in ("delivered", "closed", "cancelled")
        ):
            due = order._fix_amount_due()
            if due <= (order.credit_released_amount or 0.0) + 0.005:
                continue
            released = order.credit_released_amount or 0.0
            order._guarded().write(
                {
                    "payment_settlement_state": "unpaid",
                    "credit_released_by": False,
                    "credit_released_at": False,
                    "credit_released_amount": 0.0,
                }
            )
            order.message_post(
                body="Credit release of BDT %.2f voided: BDT %.2f is due now. Release it on "
                "credit again for the new amount, or take the payment." % (released, due)
            )

    def _fix_settlement_receipts(self):
        """Confirmed fix.ar.receipt records that paid this order: those that
        name it, and the M20 receipt it was settled against."""
        self.ensure_one()
        Receipt = self.env["fix.ar.receipt"].sudo()
        receipts = Receipt.search(
            [("source_order_id", "=", self.id), ("state", "=", "confirmed")], order="id"
        )
        if (
            self.payment_settlement_state == "settled"
            and self.settlement_verified
            and self.invoice_ref
            and self.settlement_source in ("m20_receipt", "field_collection")
        ):
            partner = self.customer_id.commercial_partner_id
            receipts |= Receipt.search(
                [
                    ("state", "=", "confirmed"),
                    ("source_order_id", "in", (False, self.id)),
                    "|",
                    ("name", "=", self.invoice_ref),
                    ("reference", "=", self.invoice_ref),
                ]
            ).filtered(lambda r: r.customer_id.commercial_partner_id == partner)[:1]
        return receipts

    def _fix_advances_held(self) -> float:
        """Advances the customer already paid on this order (confirmed)."""
        self.ensure_one()
        if not self.id:
            return 0.0
        receipts = (
            self.env["fix.ar.receipt"]
            .sudo()
            .search(
                [
                    ("source_order_id", "=", self.id),
                    ("state", "=", "confirmed"),
                    ("is_order_advance", "=", True),
                ]
            )
        )
        return round(sum(receipts.mapped("amount")), 2)

    def _fix_amount_due(self) -> float:
        """What the customer still pays to settle: the governing estimate less
        the advances already received on the order (A02 ERP audit M04-F7: a
        paid diagnostic fee was charged again in the repair settlement)."""
        due = super()._fix_amount_due()
        if due <= 0:
            return due
        return max(round(due - self._fix_advances_held(), 2), 0.0)

    def _fix_link_m20_receipt(self, receipt):
        """An M20 receipt that settled this order is linked to it, so a later
        top-up or the invoice finds every receipt of the order."""
        self.ensure_one()
        if receipt and not receipt.source_order_id:
            receipt.sudo()._guarded().write({"source_order_id": self.id})

    # ---------------------------------------------------------- tax point
    def action_deliver(self):
        result = super().action_deliver()
        for order in self.filtered(lambda o: o.state == "delivered"):
            order._fix_invoice_at_delivery()
        return result

    def action_complete_onsite(self, field_order):
        """D4: an on-site job is delivered at field completion, so its tax
        invoice is raised there and the field receipt is applied to it."""
        result = super().action_complete_onsite(field_order)
        if self.state == "delivered":
            self._fix_invoice_at_delivery()
        return result

    def action_bill_refused_repair(self):
        """D6 (M01-03): the customer refuses a repair that is done (QC /
        Ready). The customer owes the approved estimate: a Service Supervisor
        raises its tax invoice now (the money already taken is applied to
        it); the order can then be cancelled as declined without a refund.
        A waiver is the goodwill approval, not this action."""
        from odoo.addons.cd_service_order.models.fix_service_order import GROUP_SUPERVISOR

        if not (self.env.su or self.env.user.has_group(GROUP_SUPERVISOR)):
            raise UserError("Only a Service Supervisor bills a refused repair.")
        Invoice = self.env["fix.ar.invoice"].sudo()
        for order in self:
            invoice = Invoice.with_company(order.company_id).from_refused_service_order(order)
            order.message_post(
                body="Refused repair billed by %s: invoice %s (BDT %.2f) for the approved "
                "estimate." % (self.env.user.name, invoice.name, invoice.total_payable)
            )
        return True

    # ------------------------------------------------- declined repair (FR-SRM-029)
    _DECLINE_REASONS = ("customer_declined", "estimate_declined")

    def action_cancel(self, reason_code=None, note=None, reason=None):
        result = super().action_cancel(reason_code=reason_code, note=note, reason=reason)
        for order in self.filtered(
            lambda o: o.state == "cancelled" and o.cancel_reason_code in self._DECLINE_REASONS
        ):
            order._fix_invoice_declined_fee()
        return result

    def _fix_invoice_declined_fee(self):
        """Charge the declined repair its diagnostic fee (SP-013 step 19): the
        paid fee stopped being the customer's credit and became the price of
        the diagnosis. A refusal (credit hold, no charge code, unconfigured
        GL) never undoes the cancellation: the order's chatter says why and
        finance retries with Invoice Diagnostic Fee."""
        self.ensure_one()
        Invoice = self.env["fix.ar.invoice"].sudo().with_company(self.company_id)
        try:
            with self.env.cr.savepoint():
                invoice = Invoice.from_declined_service_order(self)
        except UserError as exc:
            _logger.info("declined-repair fee invoice deferred for %s: %s", self.name, exc)
            self.message_post(
                body="Diagnostic fee not invoiced (%s); it stays as the customer's credit until "
                "finance runs Invoice Diagnostic Fee." % (exc.args[0] if exc.args else exc)
            )
            return False
        if invoice:
            self.message_post(
                body="Repair declined: diagnostic fee invoiced as %s (BDT %.2f), paid from the "
                "fee taken at intake." % (invoice.name, invoice.total_payable)
            )
        return invoice

    def action_invoice_diagnostic_fee(self):
        """Finance's retry of a declined repair's diagnostic-fee invoice."""
        if not self.env.user.has_group("account.group_account_manager"):
            raise AccessError("Only a finance manager invoices a declined repair's fee.")
        for order in self:
            if order.state != "cancelled" or order.cancel_reason_code not in self._DECLINE_REASONS:
                raise UserError("%s is not a declined repair." % order.name)
            invoice = (
                self.env["fix.ar.invoice"]
                .sudo()
                .with_company(order.company_id)
                .from_declined_service_order(order)
            )
            if not invoice:
                raise UserError("%s holds no diagnostic fee to invoice." % order.name)
        return True

    def _fix_invoice_at_delivery(self):
        """Raise the order's tax invoice now; a refusal (zero-charge job,
        credit hold, an unconfigured GL) never undoes the hand-over: the
        close drain retries, and the order's chatter says why."""
        self.ensure_one()
        if self._fix_zero_charge_basis() or self.payment_settlement_state == "covered_zero_charge":
            return False
        Invoice = self.env["fix.ar.invoice"].sudo()
        try:
            with self.env.cr.savepoint():
                invoice = Invoice.from_closed_service_order(self, fields.Datetime.now())
        except Exception as exc:
            _logger.info("invoice at delivery deferred for %s: %s", self.name, exc)
            self.message_post(
                body="Tax invoice not raised at delivery (%s); it is raised when the order "
                "closes." % (exc.args[0] if getattr(exc, "args", None) else exc)
            )
            return False
        self.message_post(body="Tax invoice %s raised at delivery." % invoice.name)
        return invoice


class FixEstimateInvoiceVat(models.Model):
    """The estimate charges the VAT its invoice will charge.

    The estimate took VAT once on the header (subtotal x rate, unrounded);
    the invoice (from_closed_service_order) allocates the header discount
    over the lines and rounds VAT half-up per line, as M51 requires. The
    customer settled the estimate's grand total, so any paisa between the
    two left the invoice open on a few paisa (aged, dunned) or the receipt
    over-applied (A02 ERP review, 20 Nov 2026). The estimate now computes
    its VAT the invoice's way, so what is collected is what is invoiced."""

    _inherit = "fix.estimate"

    def _fix_m51_lines(self):
        """The estimate's lines as the invoice will bill them: gross, the
        header discount allocated pro rata (allocate_discount), product code."""
        self.ensure_one()
        lines = list(self.line_ids)
        grosses = [
            (Decimal(str(line.quantity or 1)) * Decimal(str(line.unit_price or 0.0))).quantize(
                TWO_PLACES, ROUND_HALF_UP
            )
            for line in lines
        ]
        total = sum(grosses, Decimal("0"))
        discount = Decimal(str(self.discount or 0.0))
        if total <= 0 or discount > total:
            return lines, grosses, None  # the estimate's own constraint refuses it
        shares = allocate_discount(grosses, discount)
        tax_lines = [
            tax_logic.TaxLine(
                product_code=line.product_id.default_code or "SVC",
                qty=Decimal(str(line.quantity or 1)),
                unit_price=Decimal(str(line.unit_price or 0.0)),
                discount=share,
            )
            for line, share in zip(lines, shares, strict=True)
        ]
        return lines, grosses, tax_lines

    def _fix_m51_determination(self):
        """X5-03 (D23): M51's determination of this estimate's lines on the
        Dhaka day, for the order's company - the one the invoice makes at
        delivery. None where M51 cannot answer (the header rate stands in,
        and the invoice will say why)."""
        self.ensure_one()
        lines, _grosses, tax_lines = self._fix_m51_lines()
        if not tax_lines:
            return lines, None
        company = self.order_id.company_id or self.company_id or self.env.company
        try:
            det = m51_determine(
                self.env, tax_lines, on_date=dhaka_date(fields.Datetime.now()), company=company
            )
        except (UserError, ValidationError) as exc:
            _logger.info("M51 refused the VAT of estimate %s: %s", self.id, exc)
            return lines, None
        if len(det.lines) != len(lines):
            return lines, None
        return lines, det

    def _fix_line_vat_rates(self) -> dict:
        self.ensure_one()
        lines, det = self._fix_m51_determination()
        if det is None:
            return super()._fix_line_vat_rates()
        return {line.id: float(d.rate) for line, d in zip(lines, det.lines, strict=True)}

    @api.depends(
        "line_ids.line_total",
        "line_ids.line_type",
        "line_ids.quantity",
        "line_ids.unit_price",
        "line_ids.product_id",
        "discount",
        "vat_rate",
    )
    def _compute_totals(self):
        """X5-03 (owner decision D23): ONE VAT source. The estimate's VAT is
        M51's per-line determination, the same the Mushak 6.3 makes from it
        (from_closed_service_order), so the estimate's grand total is the
        invoice's total: a zero-rated or reduced item is charged as M51 says,
        never by a header rate typed on the estimate."""
        super()._compute_totals()
        for est in self:
            if not est.line_ids:
                continue
            lines, grosses, tax_lines = est._fix_m51_lines()
            if not tax_lines:
                continue
            total = sum(grosses, Decimal("0"))
            subtotal = total - Decimal(str(est.discount or 0.0)).quantize(TWO_PLACES, ROUND_HALF_UP)
            _lines, det = est._fix_m51_determination()
            if det is not None:
                vat = sum((Decimal(str(d.vat_amount)) for d in det.lines), Decimal("0"))
            else:
                # M51 cannot answer: the standard rate, rounded per line as
                # the invoice would (the invoice itself refuses until M51 can)
                rate = Decimal(str(est.vat_rate or 0.0))
                vat = sum(
                    (
                        (
                            (tl.unit_price * tl.qty).quantize(TWO_PLACES, ROUND_HALF_UP)
                            - tl.discount
                        ).quantize(TWO_PLACES, ROUND_HALF_UP)
                        * rate
                        / Decimal("100")
                    ).quantize(TWO_PLACES, ROUND_HALF_UP)
                    for tl in tax_lines
                )
            est.vat_amount = float(vat)
            est.grand_total = float(subtotal + vat)

    def write(self, vals):
        result = super().write(vals)
        # M01-04: a raised price voids a credit release given on the old one
        self.mapped("order_id")._fix_check_credit_release()
        return result

    def action_approve(self):
        result = super().action_approve()
        self.mapped("order_id")._fix_check_credit_release()
        return result
