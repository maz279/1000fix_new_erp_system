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
from odoo.exceptions import UserError

from .fix_billing_engine import TWO_PLACES, allocate_discount
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

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"credit_released_by", "credit_released_at"}

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
            exposure += sum(o._fix_amount_due() for o in others if o.id not in invoiced)
        return round(exposure, 2)

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

    @api.depends(
        "line_ids.line_total",
        "line_ids.line_type",
        "line_ids.quantity",
        "line_ids.unit_price",
        "discount",
        "vat_rate",
    )
    def _compute_totals(self):
        super()._compute_totals()
        for est in self:
            if not est.line_ids:
                continue
            grosses = [
                (Decimal(str(line.quantity or 1)) * Decimal(str(line.unit_price or 0.0))).quantize(
                    TWO_PLACES, ROUND_HALF_UP
                )
                for line in est.line_ids
            ]
            total = sum(grosses, Decimal("0"))
            discount = Decimal(str(est.discount or 0.0))
            if total <= 0 or discount > total:
                continue  # the estimate's own constraint refuses it
            rate = Decimal(str(est.vat_rate or 0.0))
            vat = Decimal("0")
            for gross, share in zip(grosses, allocate_discount(grosses, discount), strict=True):
                taxable = (gross - share).quantize(TWO_PLACES, ROUND_HALF_UP)
                vat += (taxable * rate / Decimal("100")).quantize(TWO_PLACES, ROUND_HALF_UP)
            subtotal = total - discount.quantize(TWO_PLACES, ROUND_HALF_UP)
            est.vat_amount = float(vat)
            est.grand_total = float(subtotal + vat)
