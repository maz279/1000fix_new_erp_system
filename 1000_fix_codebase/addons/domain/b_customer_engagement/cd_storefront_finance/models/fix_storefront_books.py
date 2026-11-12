# cd_storefront_finance — the storefront order's hand-off to the books.
#
# E2E3 flow 4 (12 Nov 2026, copy of fix_real): a paid, delivered and refunded
# storefront order produced no invoice, no Mushak 6.3, no revenue, no output
# VAT, no stock-out and no restock. Its M20 receipt sat unapplied as a
# customer credit, and the refund's native out_refund debited revenue that was
# never credited and wrote a 6.7 with no 6.3, outside the M20 sub-ledger
# (E3-08).
#
# An order now reaches the books through the estate's own engines, as the
# system on the acting user's behalf (a storefront operator or payment officer
# holds no accounting role):
#   invoice  at the tax point - payment confirmed, or dispatch for cash on
#            delivery (the 6.3 goes with the goods) - an M20 fix.ar.invoice
#            is raised and issued through the billing engine's source API
#            (_fix_ar_invoice_from_source): its number, the Mushak 6.3 from
#            the statutory series and the register service, the GL through
#            M19 (Dr AR / Cr revenue / Cr VAT output). The lines are the
#            order's own, at the order's prices; the price is VAT-inclusive
#            (what the customer paid), split by M51's determination.
#   receipt  the M20 receipt that proved the payment is applied to that
#            invoice (fix.ar.allocation); a payment proved by the signed
#            gateway callback is first captured as an M20 receipt on the
#            channel clearing (Dr channel / Cr AR), as AR receipts are. Cash
#            on delivery is captured on the verified delivery (G2): a courier
#            delivery as an M20 cod receipt (Dr COD clearing / Cr AR, which
#            M50's rider settlement clears against cash or bank), a branch
#            pickup as a cash receipt.
#   stock    when the order is dispatched - the goods leave the store - each
#            line's spare part leaves the M15 ledger at its average cost and
#            books its valuation suspense row, as every other issue does.
# A cancelled paid order is credited in full through an M20 credit note; a
# return restocks and is refunded by an M20 credit note
# (fix_storefront_refund_books.py).
#
# Fail closed, never blocking (the counter-sale bridge's pattern): a step
# that cannot post - an account that does not resolve, a location nobody
# named - is rolled back on its own savepoint; the order goes on, is marked
# pending with the reason, and Retry Posting or the hourly job posts it once
# the cause is fixed. Every step checks its own link first and the order row
# is locked while it posts, so nothing posts twice.
from __future__ import annotations

import logging
from decimal import ROUND_HALF_UP, Decimal
from types import SimpleNamespace

from odoo import api, fields, models
from odoo.addons.cd_billing_engine.models import fix_billing_engine as billing
from odoo.addons.cd_inventory.models.fix_inventory_approval import (
    COST_GROUP,
    check_quantity,
    location_class,
)
from odoo.addons.cd_storefront.models.fix_storefront_refund import (
    GROUP_OPERATOR,
    GROUP_PAYMENT,
    GROUP_REFUND_APPROVER,
)
from odoo.exceptions import UserError

from .fix_engine_ext import SOURCE

_logger = logging.getLogger(__name__)

CENT = Decimal("0.01")
DHAKA = "Asia/Dhaka"

# The account storefront product revenue is credited to. Unset: the billing
# engine's revenue role (cd_billing_engine.account_code.revenue), what every
# AR invoice credits. Set to a code that is not in the chart: fail closed.
REVENUE_PARAM = "cd_storefront_finance.account_code.revenue"
# The M15 location storefront orders ship from when the order names none.
LOCATION_PARAM = "cd_storefront_finance.stock_location_code"

# the order's payment rail -> the M20 receipt method (and so the clearing
# account) a gateway capture is booked as
RAIL_RECEIPT_METHOD = {"bkash": "bkash", "nagad": "nagad", "sslcommerz": "card"}

POSTING_STATES = [
    ("none", "Nothing to Post"),
    ("pending", "Pending Posting"),
    ("posted", "Posted"),
]
LINE_STOCK_STATES = [
    ("none", "Not Evaluated"),
    ("not_required", "No Stock Item"),
    ("pending", "Pending"),
    ("issued", "Issued"),
    ("returned", "Returned"),
    ("cancelled", "Not Needed (returned before issue)"),
]
LEG_LABELS = {
    "invoice": "M20 invoice / Mushak 6.3",
    "invoice_gl": "Invoice GL entry",
    "receipt": "Receipt application",
    "stock": "Stock issue",
    "cancel_credit": "Cancellation credit note",
}
RETRY_GROUPS = (
    GROUP_OPERATOR,
    GROUP_PAYMENT,
    GROUP_REFUND_APPROVER,
    "account.group_account_user",
    "account.group_account_manager",
)
ORDER_POSTING_FIELDS = {
    "posting_state",
    "posting_note",
    "posting_attempted_at",
    "ar_invoice_id",
    "ar_receipt_id",
    "ar_credit_note_id",
    "dispatched_at",
}


def _is_nid(value) -> bool:
    """BRU-ARB-07: a National ID is 10 (smart card), 13 or 17 digits."""
    value = (value or "").strip()
    return value.isdigit() and len(value) in (10, 13, 17)


def _message(exc) -> str:
    return str(exc.args[0]) if getattr(exc, "args", None) else str(exc)


def find_account(env, company, code):
    return (
        env["account.account"]
        .sudo()
        .with_company(company)
        .search([("code", "=", code), ("company_ids", "in", company.id)], limit=1)
    )


def request_credit_note(source, invoice, amount, reason_code, body):
    """An M20 credit note against `invoice`, raised for `source` and SUBMITTED
    into M20's own ladder (a second Accountant, the Accounting Administrator
    above the band): nothing is approved or issued here. Where the hand-back
    fields exist (cd_settlement_ext) the note carries its source, so the
    storefront.refund_approved consumer finds it and raises nothing twice."""
    CreditNote = source.env["fix.credit.note"].sudo()
    if reason_code not in dict(CreditNote._fields["reason_code"].selection):
        reason_code = "return"
    vals = {
        "company_id": invoice.company_id.id,
        "operating_unit_id": invoice.operating_unit_id.id,
        "invoice_id": invoice.id,
        "amount": amount,
        "reason_code": reason_code,
    }
    if "source_model" in CreditNote._fields:
        vals.update(
            {
                "customer_id": invoice.customer_id.id,
                "source_model": source._name,
                "source_id": source.id,
                "source_amount": amount,
            }
        )
    note = CreditNote.create(vals)
    note.message_post(body=body)
    note.action_submit()
    return note


class FixStorefrontOrderBooks(models.Model):
    _inherit = "fix.storefront.order"

    posting_state = fields.Selection(
        POSTING_STATES,
        string="Books",
        default="none",
        required=True,
        readonly=True,
        copy=False,
        index=True,
        help="Whether the order reached M20, the VAT register, the GL and the stock ledger. "
        "Pending: something could not post yet - see the note; the hourly job and Retry "
        "Posting post it once the cause is fixed.",
    )
    posting_note = fields.Text(string="Posting Note", readonly=True, copy=False)
    posting_attempted_at = fields.Datetime(string="Last Posting Run", readonly=True, copy=False)
    dispatched_at = fields.Datetime(string="Dispatched At", readonly=True, copy=False)
    ar_invoice_id = fields.Many2one(
        "fix.ar.invoice",
        string="M20 Invoice",
        readonly=True,
        copy=False,
        index=True,
        ondelete="restrict",
        help="The AR invoice of this order: its Mushak 6.3, revenue and output VAT.",
    )
    ar_invoice_state = fields.Selection(related="ar_invoice_id.state", string="Invoice State")
    mushak_id = fields.Many2one(
        related="ar_invoice_id.mushak_id", string="Mushak 6.3", readonly=True
    )
    ar_receipt_id = fields.Many2one(
        "fix.ar.receipt",
        string="Applied M20 Receipt",
        readonly=True,
        copy=False,
        index=True,
        ondelete="restrict",
        help="The M20 receipt applied to the invoice: the one the payment was confirmed "
        "against, or the one the bridge captured for a gateway payment.",
    )
    ar_credit_note_id = fields.Many2one(
        "fix.credit.note",
        string="Cancellation Credit Note",
        readonly=True,
        copy=False,
        ondelete="restrict",
    )
    # G9 (owner decision 12 Nov 2026): high-value cash collected on delivery
    # carries the customer's NID, as counter cash does (FR-ARB-026).
    cod_customer_nid = fields.Char(
        string="Customer NID (cash above BDT 50,000)",
        copy=False,
        help="The National ID the customer showed when paying cash on delivery above the "
        "high-value threshold. Carried to the M20 receipt; final once it is booked. Empty: the "
        "customer's verified NID is used, else the receipt waits for it.",
    )
    stock_location_id = fields.Many2one(
        "fix.stock.location",
        string="Issue From Location",
        copy=False,
        index=True,
        help="The M15 location the goods leave on dispatch. Empty: the location named by "
        "cd_storefront_finance.stock_location_code, else the one store holding the part.",
    )

    # ------------------------------------------------------------ guard
    def _fix_guarded_fields(self) -> set:
        # the posting outcome is the system's: nobody types it
        return super()._fix_guarded_fields() | ORDER_POSTING_FIELDS

    def write(self, vals):
        if "cod_customer_nid" in vals:
            value = (vals["cod_customer_nid"] or "").strip()
            if value and not _is_nid(value):
                raise UserError(
                    "%r is not a National ID (10, 13 or 17 digits) - FR-ARB-026." % value
                )
            for order in self:
                if order.sudo().ar_receipt_id and order._fix_guard_differs(
                    "cod_customer_nid", vals["cod_customer_nid"], order.cod_customer_nid
                ):
                    raise UserError(
                        "Order %s: its receipt is booked; the NID it carries is final." % order.name
                    )
        if "stock_location_id" in vals and not self.env.su:
            for order in self:
                issued = order.sudo().line_ids.filtered(
                    lambda ln: ln.stock_state in ("issued", "returned")
                )
                if issued and order._fix_guard_differs(
                    "stock_location_id", vals["stock_location_id"], order.stock_location_id
                ):
                    raise UserError(
                        "Order %s: its stock is already issued; the issue location can no "
                        "longer change." % order.name
                    )
        return super().write(vals)

    @api.ondelete(at_uninstall=False)
    def _unlink_except_in_the_books(self):
        for order in self:
            if order.ar_invoice_id or order.line_ids.filtered(
                lambda ln: ln.stock_state == "issued"
            ):
                raise UserError(
                    "Storefront order %s is in the books (M20 invoice or stock): it is "
                    "cancelled or returned, never deleted." % order.name
                )

    # ------------------------------------------------------------ receipts
    def _sf_find_m20_receipt(self, reference):
        """A receipt the bridge applied to another order (a gateway capture)
        pays that order only."""
        receipt = super()._sf_find_m20_receipt(reference)
        if receipt:
            other = self.sudo().search_count(
                [("id", "!=", self.id), ("ar_receipt_id", "=", receipt.id)]
            )
            if other:
                return self.env["fix.ar.receipt"]
        return receipt

    # ------------------------------------------------------------ transitions
    def action_confirm_payment(self, payment_ref=None, rail=None):
        result = super().action_confirm_payment(payment_ref=payment_ref, rail=rail)
        self._sfb_post()
        return result

    def action_dispatch(self, carrier_consignment_id=None):
        result = super().action_dispatch(carrier_consignment_id=carrier_consignment_id)
        self.filtered(lambda o: not o.dispatched_at)._guarded().write(
            {"dispatched_at": fields.Datetime.now()}
        )
        self._sfb_post()
        return result

    def action_deliver(self):
        result = super().action_deliver()
        self._sfb_post()
        return result

    def action_cancel(self, reason=None):
        result = super().action_cancel(reason=reason)
        self._sfb_post()
        return result

    def action_retry_posting(self):
        """Post whatever the order still owes the books (idempotent)."""
        if not (self.env.su or any(self.env.user.has_group(g) for g in RETRY_GROUPS)):
            raise UserError("Only storefront or finance staff may retry an order's posting.")
        self._sfb_post()
        return True

    @api.model
    def _cron_retry_storefront_postings(self, limit=200):
        """Hourly: post every order still pending, oldest attempt first. An
        order paid before this bridge was installed is posted the same way."""
        orders = self.sudo().search(
            [
                "|",
                ("posting_state", "=", "pending"),
                "&",
                ("posting_state", "=", "none"),
                ("state", "in", ("paid", "dispatched", "delivered")),
            ],
            order="posting_attempted_at asc, id asc",
            limit=limit,
        )
        orders._sfb_post()
        returns = self.env["fix.storefront.return"]._sfb_cron_returns(limit)
        rmas = self.env["fix.storefront.rma"]._sfb_cron_returns(limit)
        return len(orders) + returns + rmas

    # ---------------------------------------------------------------- engine
    def _sfb_post(self):
        for order in self:
            if order.state != "draft":
                order._sfb_post_one()

    def _sfb_todo(self):
        """The steps the order still owes, in order."""
        self.ensure_one()
        legs = []
        inv = self.ar_invoice_id
        if self.state == "cancelled":
            if inv and inv.state in ("issued", "paid") and not self.ar_credit_note_id:
                legs.append("cancel_credit")
            return legs
        money = (self.total_amount or 0.0) > 0.005
        shipped = self.state in ("dispatched", "delivered")
        if money and (self.state == "paid" or shipped):
            if not inv:
                legs.append("invoice")
            elif inv.state in ("issued", "paid") and not inv.posted_move_id:
                legs.append("invoice_gl")
            if self._sfb_receipt_owed():
                legs.append("receipt")
        if shipped and self.line_ids.filtered(lambda ln: ln.stock_state in ("none", "pending")):
            legs.append("stock")
        return legs

    def _sfb_receipt_owed(self) -> bool:
        inv = self.ar_invoice_id
        if not inv or inv.state != "issued" or inv.amount_residual <= 0.005:
            return False
        if self.payment_date:
            return True
        # cash on delivery: the cash is collected at the door
        return self.payment_rail == "cod" and self.state == "delivered"

    def _sfb_post_one(self):
        """Run every step the order owes on its own savepoint, as the system
        on behalf of the acting user (env.uid stays the operator / officer)."""
        self.ensure_one()
        order = self.sudo().with_company(self.company_id)
        self.env.flush_all()
        # one runner per order: a concurrent retry waits, then finds nothing to do
        self.env.cr.execute(
            "SELECT id FROM fix_storefront_order WHERE id = %s FOR UPDATE", [order.id]
        )
        order.invalidate_recordset()
        problems, tried = [], set()
        while True:
            todo = [leg for leg in order._sfb_todo() if leg not in tried]
            if not todo:
                break
            leg = todo[0]
            tried.add(leg)
            if leg == "stock":
                # one savepoint per line: a line that cannot leave never holds
                # back the others
                problems += order._sfb_leg_stock()
                continue
            try:
                with self.env.cr.savepoint():
                    getattr(order, "_sfb_leg_%s" % leg)()
            except Exception as exc:
                if not isinstance(exc, UserError | ValueError):
                    _logger.exception("storefront order %s: %s step failed", order.name, leg)
                problems.append("%s: %s" % (LEG_LABELS[leg], _message(exc)))
            self.env.invalidate_all()
        order._sfb_record(problems)

    def _sfb_record(self, problems):
        self.ensure_one()
        if self._sfb_todo():
            new = "pending"
        elif self.state in ("draft", "pending_payment") or (
            self.state == "cancelled" and not self.ar_invoice_id
        ):
            new = "none"
        else:
            new = "posted"
        note = "\n".join(problems) or False
        changed = (new, note or False) != (self.posting_state, self.posting_note or False)
        self._guarded().write(
            {
                "posting_state": new,
                "posting_note": note,
                "posting_attempted_at": fields.Datetime.now(),
            }
        )
        if changed:
            label = dict(POSTING_STATES)[new]
            body = "Books: %s." % label if not note else "Books: %s - %s" % (label, note)
            self.message_post(body=body)

    # ---------------------------------------------------------------- helpers
    def _sfb_day(self, stamp=None):
        """The Bangladesh calendar day of an order event (UTC+6 frame)."""
        tz = self.company_id.partner_id.tz or DHAKA
        return fields.Date.context_today(
            self.with_context(tz=tz), timestamp=stamp or fields.Datetime.now()
        )

    def _sfb_tax_day(self):
        """The tax point: the payment when it came first, else the dispatch.
        A tax point inside a period the close has locked moves to the first
        open day, as the billing engine dates every late statutory invoice
        (its ar_first_open_date, where the engine has it)."""
        day = self._sfb_day(self.payment_date or self.dispatched_at)
        first_open = getattr(billing, "ar_first_open_date", None)
        return first_open(self.env, self.company_id, day) if first_open else day

    def _sfb_revenue_account(self):
        """The storefront revenue account, or None for the billing engine's
        revenue role. A configured code that is not in the chart fails closed:
        it never falls through to a guess."""
        code = (self.env["ir.config_parameter"].sudo().get_param(REVENUE_PARAM) or "").strip()
        if not code:
            return None
        account = find_account(self.env, self.company_id, code)
        if not account:
            raise UserError(
                "No GL account for storefront revenue: %s names %s, which is not an account of "
                "%s. Set the system parameter %s to the account code."
                % (REVENUE_PARAM, code, self.company_id.name, REVENUE_PARAM)
            )
        return account

    def _sfb_split(self, gross, product, day):
        """[(taxable, label suffix)] whose M51-determined totals make `gross`,
        the VAT-inclusive amount the customer paid, exactly. The rate and the
        treatment are M51's (Tax Rate Master + tariff of the product code),
        determined exactly as the invoice line will determine them. When no
        taxable value reaches `gross` (an inclusive total the 2-decimal
        rounding skips) the paisa is its own line."""
        Line = self.env["fix.ar.invoice.line"].sudo()
        no_treatment = self.env["fix.vat.treatment"]
        frame = SimpleNamespace(invoice_date=day, company_id=self.company_id)

        def determine(taxable):
            det = Line._fix_determined(frame, float(taxable), product, no_treatment)
            total = Decimal(str(det.taxable_amount)) + Decimal(str(det.vat_amount))
            return det, total.quantize(CENT, ROUND_HALF_UP)

        def exact(total):
            probe, _ = determine(total)
            if probe.treatment == "truncated":
                raise UserError(
                    "%s is a truncated-base supply: its VAT is not a rate on the storefront "
                    "price. Raise its Mushak 6.3 through billing." % product.display_name
                )
            rate = Decimal(str(probe.rate))
            net = (total * 100 / (100 + rate)).quantize(CENT, ROUND_HALF_UP)
            for taxable in (net, net - CENT, net + CENT):
                if taxable >= 0 and determine(taxable)[1] == total:
                    return taxable
            return None

        taxable = exact(gross)
        if taxable is not None:
            return [(taxable, "")]
        taxable = exact(gross - CENT)
        if taxable is None or determine(CENT)[1] != CENT:
            raise UserError(
                "No taxable value of %s makes the VAT-inclusive %s exactly: raise its invoice "
                "through billing." % (product.display_name, gross)
            )
        return [(taxable, ""), (CENT, " (rounding of the VAT-inclusive price)")]

    def _sfb_invoice_lines(self, day):
        lines = []
        for line in self.line_ids:
            gross = Decimal(str(line.subtotal or 0.0)).quantize(CENT, ROUND_HALF_UP)
            if gross <= 0:
                continue
            product = line.product_id.sudo().product_variant_id
            qty = format(Decimal(str(line.quantity)).normalize(), "f")
            label = "%s x %s (storefront order %s)" % (line.product_id.display_name, qty, self.name)
            for taxable, suffix in self._sfb_split(gross, product, day):
                lines.append(
                    {
                        "description": label + suffix,
                        "taxable_amount": float(taxable),
                        "product_id": product.id if not suffix else False,
                    }
                )
        return lines

    # ---------------------------------------------------------------- steps
    def _sfb_leg_invoice(self):
        """The M20 invoice, issued as the billing engine issues every system
        invoice: number, Mushak 6.3, GL (one call, one transaction)."""
        day = self._sfb_tax_day()
        credit_account = self._sfb_revenue_account()
        # the invoice is billed to the party the receipt came from, so the
        # receipt applies to it (M20 allocates within one customer)
        customer = self.payment_receipt_id.customer_id or self.customer_id
        lines = self._sfb_invoice_lines(day)
        if not lines:
            raise UserError("Order %s has no priced line to invoice." % self.name)
        rail = dict(self._fields["payment_rail"].selection).get(self.payment_rail)
        invoice = self.env["fix.ar.invoice"]._fix_ar_invoice_from_source(
            self,
            customer,
            lines,
            "Storefront order %s (%s)" % (self.name, rail),
            credit_account=credit_account,
            invoice_date=day,
            issue=True,
        )
        invoice = invoice.sudo()
        if invoice.state not in ("draft", "cancelled") and (
            self.currency_id.compare_amounts(invoice.total_payable, self.total_amount) != 0
        ):
            raise UserError(
                "The M20 invoice of order %s would total %.2f, not the %.2f the customer pays."
                % (self.name, invoice.total_payable, self.total_amount)
            )
        self._guarded().write({"ar_invoice_id": invoice.id})

    def _sfb_leg_invoice_gl(self):
        """The invoice was issued but its GL skipped (an account the billing
        engine could not resolve): post it now, once."""
        invoice = self.ar_invoice_id
        invoice._post_issue_gl()
        if not invoice.posted_move_id:
            raise UserError(
                "%s (storefront revenue: system parameter %s, else "
                "cd_billing_engine.account_code.revenue)."
                % (invoice.gl_note or "The invoice is not posted to the GL", REVENUE_PARAM)
            )

    def _sfb_capture_gateway_receipt(self):
        """The signed gateway callback proved the capture: book it as the M20
        receipt it is, on the rail's channel clearing (Dr channel / Cr AR)."""
        method = RAIL_RECEIPT_METHOD.get(self.payment_rail)
        if not method:
            raise UserError(
                "Order %s was paid on %s, which has no M20 receipt method."
                % (self.name, self.payment_rail)
            )
        invoice = self.ar_invoice_id
        receipt = (
            self.env["fix.ar.receipt"]
            .sudo()
            .create(
                {
                    "company_id": self.company_id.id,
                    "operating_unit_id": invoice.operating_unit_id.id,
                    "customer_id": invoice.customer_id.id,
                    "currency_id": self.currency_id.id,
                    "amount": self.total_amount,
                    "method": method,
                    "reference": self.payment_ref,
                    "receipt_date": self._sfb_day(self.payment_date),
                }
            )
        )
        receipt.message_post(
            body="Captured by the storefront bridge from the verified %s callback of order %s "
            "(TrxID %s)." % (self.payment_rail, self.name, self.payment_ref)
        )
        receipt.action_confirm()
        return receipt

    def _sfb_capture_cod_receipt(self):
        """G2 (owner decision 12 Nov 2026): a cash-on-delivery order is paid
        at the door, against the proof of delivery. The cash is booked once,
        as the M20 receipt that closes the invoice:

        * a courier delivery: method cod, Dr COD clearing / Cr AR. The rider
          owes the cash until M50's COD settlement remits it (Dr cash or bank /
          Cr COD clearing), which touches no receivable;
        * a branch pickup: the cash is in the branch's hand, method cash
          (Dr cash / Cr AR). A cash receipt the cashier already captured for
          the order (reference = the order number; e.g. with the customer NID
          the high-value cash rule asks for) is used instead.

        An account that does not resolve refuses the confirmation; the order
        stays pending with that reason and the retry books it once."""
        invoice = self.ar_invoice_id
        counter = self.shipping_method == "branch_pickup" or not self.carrier_consignment_id
        if counter:
            found = self._sf_find_m20_receipt(self.name)
            if found:
                return found
        nid = self._sfb_high_value_nid()
        receipt = (
            self.env["fix.ar.receipt"]
            .sudo()
            .create(
                {
                    "company_id": self.company_id.id,
                    "operating_unit_id": invoice.operating_unit_id.id,
                    "customer_id": invoice.customer_id.id,
                    "currency_id": self.currency_id.id,
                    "amount": self.total_amount,
                    "method": "cash" if counter else "cod",
                    "reference": self.name,
                    "receipt_date": self._sfb_day(self.delivered_at),
                    "nid_captured": nid or False,
                }
            )
        )
        consignment = self.carrier_consignment_id.sudo()
        if counter:
            how = "handed over at the branch counter"
        else:
            how = "delivered on consignment %s%s" % (
                consignment.name,
                (" by rider %s" % consignment.rider_id.name)
                if "rider_id" in consignment._fields and consignment.rider_id
                else (" by courier %s" % consignment.courier_partner_id.name)
                if "courier_partner_id" in consignment._fields and consignment.courier_partner_id
                else "",
            )
        receipt.message_post(
            body="Cash on delivery of storefront order %s, %s: captured by the storefront "
            "bridge on the verified delivery." % (self.name, how)
        )
        try:
            receipt.action_confirm()
        except UserError as exc:
            hint = (
                " Or record the cash as a confirmed M20 receipt of the customer with reference "
                "%s, then retry." % self.name
                if counter
                else ""
            )
            raise UserError(
                "Cash on delivery of %s: %s%s" % (self.name, _message(exc), hint)
            ) from exc
        return receipt

    # ------------------------------------------------- G9: high-value cash NID
    def _sfb_customer_verified_nid(self) -> str:
        """The customer's NID verified in KYC (M33 identity document, verified
        by a data steward), read through the residency client: the number
        lives in Z4 only. Empty when there is none or Z4 does not answer."""
        if "fix.identity.document" not in self.env:
            return ""
        customer = self.customer_id
        docs = (
            self.env["fix.identity.document"]
            .sudo()
            .search(
                [
                    ("partner_id", "in", (customer | customer.commercial_partner_id).ids),
                    ("document_type", "in", ("nid_10", "nid_17")),
                    ("verification_status", "=", "verified"),
                ],
                order="is_primary desc, id desc",
            )
        )
        for row in docs.read(["document_number"]):
            nid = "".join(ch for ch in str(row.get("document_number") or "") if ch.isdigit())
            if _is_nid(nid):
                return nid
        return ""

    def _sfb_high_value_nid(self) -> str:
        """G9 (owner decision 12 Nov 2026): cash above the high-value
        threshold (FR-ARB-026, cd_billing_engine.nid_cash_threshold, BDT
        50,000) is booked with the customer's NID, whether the counter or a
        courier took it. The NID recorded on the order, else the customer's
        verified NID. None found: refused with the reason, so the order stays
        pending and nothing is booked until it is recorded."""
        self.ensure_one()
        threshold = self.env["fix.ar.receipt"]._nid_threshold()
        if (self.total_amount or 0.0) <= threshold:
            return ""
        nid = (self.cod_customer_nid or "").strip() or self._sfb_customer_verified_nid()
        if not nid:
            raise UserError(
                "Cash on delivery of %s: %.2f is above the BDT %s high-value cash limit and no "
                "customer NID is recorded (FR-ARB-026). Record the customer's National ID on the "
                "order (Record Customer NID), or verify one on the customer; the receipt is "
                "booked on the next retry." % (self.name, self.total_amount, threshold)
            )
        return nid

    def action_record_customer_nid(self, nid=None):
        """Record the National ID the customer showed at delivery (G9), then
        post what the order still owes. Final once its receipt is booked."""
        if not (self.env.su or any(self.env.user.has_group(g) for g in RETRY_GROUPS)):
            raise UserError("Only storefront or finance staff may record a customer's NID.")
        value = "".join(ch for ch in str(nid or "") if not ch.isspace())
        if not _is_nid(value):
            raise UserError(
                "%r is not a National ID (10, 13 or 17 digits) - FR-ARB-026." % (nid or "")
            )
        for order in self:
            if order.sudo().ar_receipt_id:
                raise UserError(
                    "Order %s: its receipt is booked; the NID it carries is final." % order.name
                )
            order.sudo().write({"cod_customer_nid": value})
            order.sudo().message_post(body="Customer NID recorded for the high-value cash rule.")
        self._sfb_post()
        return True

    def _sfb_cod_receipt_elsewhere(self) -> bool:
        """M50's COD settlement asks: was this order's receivable settled by
        money that did not land in COD clearing (a prepayment, a counter cash
        receipt)? Then a rider settlement must not count it again."""
        self.ensure_one()
        receipt = self.sudo().ar_receipt_id
        return bool(receipt) and receipt.method != "cod"

    def _sfb_leg_receipt(self):
        """Apply the order's receipt to its invoice (never a credit left
        floating on the customer)."""
        invoice = self.ar_invoice_id
        receipt = self.ar_receipt_id or self.payment_receipt_id
        if not receipt:
            # _sfb_receipt_owed: no payment date means a delivered COD order
            receipt = (
                self._sfb_capture_gateway_receipt()
                if self.payment_date
                else self._sfb_capture_cod_receipt()
            )
        if receipt != self.ar_receipt_id:
            self._guarded().write({"ar_receipt_id": receipt.id})
        receipt = receipt.sudo()
        if receipt.state != "confirmed":
            raise UserError(
                "Receipt %s is %s: it cannot be applied." % (receipt.name, receipt.state)
            )
        if receipt.customer_id != invoice.customer_id:
            raise UserError(
                "Receipt %s is from %s, invoice %s is to %s: apply it by hand."
                % (
                    receipt.name,
                    receipt.customer_id.display_name,
                    invoice.name,
                    invoice.customer_id.display_name,
                )
            )
        amount = round(min(receipt.unapplied_amount, invoice.amount_residual), 2)
        if amount <= 0.005:
            raise UserError(
                "Receipt %s has nothing unapplied left for invoice %s: apply another receipt "
                "to it." % (receipt.name, invoice.name)
            )
        self.env["fix.ar.allocation"].sudo().create(
            {
                "receipt_id": receipt.id,
                "invoice_id": invoice.id,
                "amount": amount,
                "company_id": invoice.company_id.id,
                "operating_unit_id": invoice.operating_unit_id.id,
            }
        )

    def _sfb_leg_cancel_credit(self):
        """A cancelled paid order: the whole invoice is credited through M20
        (6.7, GL mirror, the money back through treasury once issued)."""
        invoice = self.ar_invoice_id
        amount = round(invoice.total_payable - invoice.credited_amount, 2)
        if amount <= 0.005:
            return
        note = request_credit_note(
            self,
            invoice,
            amount,
            "order_cancelled",
            "Raised by the storefront bridge: order %s was cancelled after payment; credit of "
            "BDT %.2f against invoice %s, for finance to approve and issue."
            % (self.name, amount, invoice.name),
        )
        self._guarded().write({"ar_credit_note_id": note.id})

    # ---------------------------------------------------------------- stock
    def _sfb_leg_stock(self):
        problems = []
        for line in self.line_ids.filtered(lambda ln: ln.stock_state in ("none", "pending")):
            try:
                with self.env.cr.savepoint():
                    line._sfb_issue()
            except Exception as exc:
                if not isinstance(exc, UserError | ValueError):
                    _logger.exception("storefront order %s: stock issue failed", self.name)
                problems.append(
                    "%s (%s): %s"
                    % (LEG_LABELS["stock"], line.product_id.display_name, _message(exc))
                )
                self.env.invalidate_all()
                if line.stock_state == "none":
                    line.sudo().write({"stock_state": "pending"})
        return problems


class FixStorefrontOrderLineBooks(models.Model):
    _inherit = "fix.storefront.order.line"

    stock_state = fields.Selection(
        LINE_STOCK_STATES, string="Stock", default="none", required=True, readonly=True, copy=False
    )
    stock_part_id = fields.Many2one(
        "fix.spare.part", string="Spare Part", readonly=True, copy=False
    )
    stock_location_id = fields.Many2one(
        "fix.stock.location", string="Issued From", readonly=True, copy=False
    )
    stock_ownership_class = fields.Char(string="Issued From Class", readonly=True, copy=False)
    stock_unit_cost = fields.Float(
        string="Issue Unit Cost (BDT)", readonly=True, copy=False, groups=COST_GROUP
    )
    stock_serial = fields.Char(
        string="Serial Sold",
        readonly=True,
        copy=False,
        help="The serial of a serialized part, recorded by an operator before dispatch.",
    )
    stock_lot_id = fields.Many2one(
        "fix.stock.lot", string="Issued Serial", readonly=True, copy=False
    )

    def action_set_stock_serial(self, serial):
        """A storefront operator records the serial of a serialized part
        before it ships (the line itself stays frozen)."""
        if not (self.env.su or self.env.user.has_group(GROUP_OPERATOR)):
            raise UserError("Recording the serial sold needs the Storefront Operator role.")
        serial = (serial or "").strip()
        for line in self:
            if line.stock_state in ("issued", "returned"):
                raise UserError("The line's stock is already issued: its serial is history.")
            line.sudo().write({"stock_serial": serial or False})
        return True

    def _sfb_part(self):
        self.ensure_one()
        company = self.order_id.company_id
        parts = (
            self.env["fix.spare.part"]
            .sudo()
            .search(
                [
                    ("product_id.product_tmpl_id", "=", self.product_id.id),
                    ("company_id", "in", [company.id, False]),
                ],
                limit=2,
            )
        )
        if len(parts) > 1:
            raise UserError(
                "%s is the product of several spare parts (%s): issue it through M15."
                % (self.product_id.display_name, ", ".join(parts.mapped("part_number")))
            )
        return parts

    def _sfb_issue_location(self, part):
        """The order's location, else the configured storefront store, else the
        ONE store of the order's company (and operating unit) holding enough
        of the part. Never a guess."""
        order = self.order_id
        if order.stock_location_id:
            return order.stock_location_id
        Location = self.env["fix.stock.location"].sudo()
        code = (self.env["ir.config_parameter"].sudo().get_param(LOCATION_PARAM) or "").strip()
        if code:
            location = Location.search(
                [("code", "=", code), ("company_id", "=", order.company_id.id)], limit=1
            )
            if not location:
                raise UserError(
                    "%s names %s, which is not a stock location of %s."
                    % (LOCATION_PARAM, code, order.company_id.name)
                )
            return location
        domain = [
            ("part_id", "=", part.id),
            ("location_id.company_id", "=", order.company_id.id),
            ("location_id.location_type", "in", ("branch", "central")),
            ("ownership_class", "=", "owned"),
            ("stock_status", "=", "unrestricted"),
        ]
        if order.operating_unit_id:
            domain.append(("location_id.operating_unit_id", "=", order.operating_unit_id.id))
        rows = (
            self.env["fix.stock.onhand"]
            .sudo()
            .search(domain)
            .filtered(lambda r: (r.qty or 0.0) - (r.reserved or 0.0) + 1e-9 >= self.quantity)
        )
        if len(rows.location_id) == 1:
            return rows.location_id
        where = ", ".join(rows.location_id.mapped("code")) or "none"
        raise UserError(
            "%s stores hold %s of %s (%s): set the order's Issue From Location (or the system "
            "parameter %s) and retry."
            % ("Several" if rows else "No", self.quantity, part.part_number, where, LOCATION_PARAM)
        )

    def _sfb_issue(self):
        """The part leaves the M15 ledger like any issue: unrestricted,
        unreserved stock of the location at its average cost, bins respected,
        a serial in stock there, and the valuation suspense row booked. A
        graded refurb device is its own ledger (reserved, then sold on
        delivery); a product with no spare part is not stock."""
        self.ensure_one()
        line = self.sudo()
        if line.graded_stock_id:
            line.write({"stock_state": "not_required"})
            return
        part = line._sfb_part()
        if not part:
            line.write({"stock_state": "not_required"})
            return
        location = line._sfb_issue_location(part)
        if location.location_type in ("quarantine", "scrap"):
            raise UserError(
                "%s is a %s location: its stock is not sold."
                % (location.code, location.location_type)
            )
        qty = line.quantity
        check_quantity(part, qty, "storefront order quantity")
        cls = location_class(location, "owned")
        lot = self.env["fix.stock.lot"]
        if part.is_serialized:
            serial = (line.stock_serial or "").strip()
            if not serial:
                raise UserError(
                    "%s is serialized: record the serial sold on the line and retry."
                    % part.part_number
                )
            if abs(qty - 1.0) > 1e-9:
                raise UserError("%s is serialized: one line ships one serial." % part.part_number)
            lot = lot._fix_find(part, serial)
            if not lot or lot.status != "in_stock" or lot.location_id != location:
                raise UserError(
                    "Serial %s of %s is not in stock at %s."
                    % (serial, part.part_number, location.code)
                )
        Onhand = self.env["fix.stock.onhand"]
        bucket = Onhand._bucket(part, location, cls)
        available = ((bucket.qty or 0.0) - (bucket.reserved or 0.0)) if bucket else 0.0
        if available + 1e-9 < qty:
            raise UserError(
                "Only %s of %s is available at %s for an order of %s."
                % (round(available, 4), part.part_number, location.code, qty)
            )
        cost = bucket.unit_cost or 0.0
        Onhand._fix_check_bins(part, location, qty)
        Onhand._apply(part, location, cls, -qty)
        if lot:
            lot._fix_move("issued", qty=0.0)
        self.env["fix.inventory.valuation.suspense"]._fix_post(
            SOURCE, part, -qty, cost, line.order_id.name, location=location, ownership=cls
        )
        line.write(
            {
                "stock_state": "issued",
                "stock_location_id": location.id,
                "stock_part_id": part.id,
                "stock_ownership_class": cls,
                "stock_unit_cost": cost,
                "stock_lot_id": lot.id or False,
            }
        )
