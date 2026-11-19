# A service order's money reaches the books (A02 ERP audit, 19 Nov 2026).
#
# On a copy of fix_real a BDT 1,150 counter settlement went into the branch
# drawer (fix.cash.shift cash_payments) and nowhere else: no GL entry, no AR
# receipt. When the order closed, M20 issued its invoice (Dr AR 1,150 /
# Cr revenue 1,000 / Cr VAT 150) and nothing paid it, so the customer who had
# paid showed BDT 1,150 owing, aged and dunned; and the M50 deposit then
# credited the drawer account for cash that had never been debited to it. The
# same held for M02 field cash and for wallet / card payments.
#
# Every VERIFIED counter or field settlement now raises a confirmed M20
# receipt for the order:
#   cash            Dr drawer cash (cd_cash_position.account_code.branch_cash,
#                   the account the M50 deposit credits) / Cr AR control
#   wallet / card   Dr the channel clearing of the receipt method / Cr AR
# posted as the system on the cashier's behalf (she holds no accounting role,
# as with the counter sale). A counter settlement is verified when taken; a
# field collection when a cashier accepts / verifies it (never the technician).
# The receipt is the order's settlement evidence: when the order is invoiced,
# the invoice applies it (fix.ar.invoice._fix_apply_order_settlement).
#
# High-value cash: the statutory NID is the M04 High-Value Cash ID Check on the
# order, which keeps only the last 4 digits; the receipt takes that check as
# its NID evidence instead of a typed number.
import pytz
from odoo import api, fields, models
from odoo.addons.cd_billing_engine.models.fix_ar_engine import _ar_account
from odoo.exceptions import UserError

from .fix_counter_sale_posting import resolve_account

# settlement tender (cd_front_desk SETTLEMENT_TENDERS) -> M20 receipt method
TENDER_RECEIPT_METHOD = {
    "cash": "cash",
    "bkash": "bkash",
    "nagad": "nagad",
    "rocket": "mobile_wallet",
    "upay": "mobile_wallet",
    "card": "card",
    "sslcommerz": "card",
}


class FixServiceOrderSettlementReceipt(models.Model):
    _inherit = "fix.service.order"

    settlement_receipt_id = fields.Many2one(
        "fix.ar.receipt",
        string="Settlement Receipt (M20)",
        readonly=True,
        copy=False,
        index=True,
        help="The M20 receipt raised for the money the counter or a field technician took: "
        "Dr drawer cash or channel clearing / Cr the customer's AR. The order's invoice "
        "applies it.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"settlement_receipt_id"}

    # ------------------------------------------------------------ triggers
    def _fix_record_settlement(self, amount_bdt, reference, source):
        if source == "counter" and fd_tender(self.env) == "cash":
            # BRU-FRD-04: high-value cash needs the customer's NID first
            Check = self.env["fix.cash.id.check"]
            for order in self:
                Check._hv_require(order, float(amount_bdt or 0.0), True)
        self.ensure_one()
        # A top-up adds to a verified settlement. The receipt books exactly the
        # money THIS call took, by THIS call's tender and reference: the order's
        # settlement_tender / settlement_source / invoice_ref describe the first
        # payment (a bKash settlement topped up in cash booked the cash to the
        # bKash clearing, and a top-up on an order first settled from an M20
        # receipt booked nothing at all; A02 ERP review, 20 Nov 2026).
        before = (
            self.amount_settled_bdt or 0.0
            if self.payment_settlement_state == "settled" and self.settlement_verified
            else 0.0
        )
        result = super()._fix_record_settlement(amount_bdt, reference, source)
        if source == "counter" and self.settlement_verified:
            taken = round((self.amount_settled_bdt or 0.0) - before, 2)
            if taken > 0.005:
                self._fdf_raise_settlement_receipt(
                    taken, tender=fd_tender(self.env), reference=reference
                )
        return result

    def action_verify_settlement(self):
        result = super().action_verify_settlement()
        self._fdf_receipt_if_verified()
        return result

    def _fdf_receipt_if_verified(self):
        """Raise the receipt for a field collection once a cashier verifies
        it (a counter settlement raises its own when it is taken)."""
        for order in self:
            if not (
                order.payment_settlement_state == "settled"
                and order.settlement_verified
                and order.settlement_source == "field_collection"
            ):
                continue
            if order._fdf_existing_m20_receipt():
                continue  # a field TrxID verified against a receipt already booked
            missing = round((order.amount_settled_bdt or 0.0) - order._fdf_settled_in_books(), 2)
            if missing > 0.005:
                order._fdf_raise_settlement_receipt(missing)

    def _fdf_settled_in_books(self) -> float:
        """What the order's settlement receipts already hold (not advances)."""
        self.ensure_one()
        receipts = (
            self.env["fix.ar.receipt"]
            .sudo()
            .search(
                [
                    ("source_order_id", "=", self.id),
                    ("state", "=", "confirmed"),
                    ("is_order_advance", "=", False),
                ]
            )
        )
        return sum(receipts.mapped("amount"))

    def _fdf_existing_m20_receipt(self):
        """A field TrxID verified against an M20 receipt already booked."""
        self.ensure_one()
        if self.settlement_source != "field_collection" or not self.invoice_ref:
            return self.env["fix.ar.receipt"]
        # the customer's own receipt only: another customer's receipt carrying
        # the same TrxID must not stand in for this order's money
        partner = self.customer_id.commercial_partner_id
        return (
            self.env["fix.ar.receipt"]
            .sudo()
            .search(
                [
                    ("state", "=", "confirmed"),
                    ("source_order_id", "in", (False, self.id)),
                    ("is_order_advance", "=", False),
                    (
                        "id",
                        "not in",
                        self.env["fix.ar.receipt"]
                        .sudo()
                        .search(
                            [("source_order_id", "=", self.id), ("is_order_advance", "=", False)]
                        )
                        .ids,
                    ),
                    "|",
                    ("name", "=", self.invoice_ref),
                    ("reference", "=", self.invoice_ref),
                ]
            )
            .filtered(lambda r: r.customer_id.commercial_partner_id == partner)[:1]
        )

    # ------------------------------------------------------------ the receipt
    def _fdf_raise_settlement_receipt(self, amount, tender=None, reference=None):
        self.ensure_one()
        amount = round(amount or 0.0, 2)
        if amount <= 0:
            return self.env["fix.ar.receipt"]
        tender = tender or self.settlement_tender or "cash"
        reference = (reference or "").strip() or self.invoice_ref
        method = TENDER_RECEIPT_METHOD.get(tender)
        if not method:
            raise UserError(
                "Order %s: tender '%s' has no M20 receipt method." % (self.name, tender)
            )
        company = self.company_id or self.env.company
        if method == "cash":
            account, why = resolve_account(self.env, company, "drawer_cash")
            if not account:
                # never take cash the books cannot hold: the settlement rolls back
                raise UserError("Settlement of %s refused: %s" % (self.name, why))
        unit = self.operating_unit_id or self.branch_id.operating_unit_id
        check = (
            self.env["fix.cash.id.check"].sudo().search([("order_id", "=", self.id)], limit=1)
            if method == "cash"
            else self.env["fix.cash.id.check"]
        )
        receipt = (
            self.env["fix.ar.receipt"]
            .sudo()
            .with_company(company)
            .create(
                {
                    "company_id": company.id,
                    "operating_unit_id": unit.id or False,
                    "branch_id": self.branch_id.id,
                    "customer_id": self.customer_id.id,
                    "amount": amount,
                    "method": method,
                    "reference": reference,
                    "receipt_date": dhaka_today(),
                    "source_order_id": self.id,
                    "cash_id_check_id": check.id or False,
                }
            )
        )
        receipt.action_confirm()
        assert_receipt_posted(receipt, "Settlement of %s" % self.name)
        if not self.settlement_receipt_id:
            self._guarded().write({"settlement_receipt_id": receipt.id})
        self.message_post(
            body="Payment of BDT %.2f (%s) posted to the books as receipt %s."
            % (
                amount,
                dict(self._fields["settlement_tender"].selection).get(tender, tender),
                receipt.name,
            )
        )
        return receipt


def fd_tender(env) -> str:
    return env.context.get("fd_settlement_tender") or "cash"


def dhaka_today():
    """The business day in Dhaka (UTC+6), whoever is signed in: a payment
    taken between 00:00 and 06:00 local belongs to that local day."""
    now = fields.Datetime.now().replace(tzinfo=pytz.UTC)
    return now.astimezone(pytz.timezone("Asia/Dhaka")).date()


def assert_receipt_posted(receipt, what):
    """Money taken for an order is on the books or not taken at all. M20
    confirms a receipt with only a gl_note when it cannot post (no AR
    control, no general journal); for counter / field money that would be
    cash in hand with no ledger entry, so the payment rolls back instead.
    A company with no AR control account at all (no GL configured) is the
    one case M20 itself records as 'not posted'."""
    if receipt.posted_move_id:
        return
    if not _ar_account(receipt.env, receipt.company_id, "ar"):
        return
    raise UserError(
        "%s refused: receipt %s could not be posted to the ledger (%s)."
        % (what, receipt.name, receipt.gl_note or "no journal entry")
    )


class FixArReceiptServiceOrder(models.Model):
    _inherit = "fix.ar.receipt"

    cash_id_check_id = fields.Many2one(
        "fix.cash.id.check", string="High-Value Cash ID Check", readonly=True, copy=False
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"cash_id_check_id"}

    def _fix_debit_account(self, role):
        if self.source_order_id and self.method == "cash":
            # the drawer: the account the M50 deposit credits
            account, why = resolve_account(self.env, self.company_id, "drawer_cash")
            if not account:
                raise UserError(why)
            return account
        return super()._fix_debit_account(role)

    def _fix_nid_evidenced_elsewhere(self) -> bool:
        check = self.cash_id_check_id
        if (
            check
            and self.source_order_id
            and check.order_id == self.source_order_id
            and check.partner_id.commercial_partner_id == self.customer_id.commercial_partner_id
            and check.amount + 0.005 >= self.amount
        ):
            return True
        return super()._fix_nid_evidenced_elsewhere()


class FixCashIdCheckServiceOrder(models.Model):
    """BRU-FRD-04 for a service order's cash: one check per order."""

    _inherit = "fix.cash.id.check"

    _order_unique = models.Constraint("UNIQUE (order_id)", "A service order has one ID check.")

    order_id = fields.Many2one(
        "fix.service.order", string="Service Order", index=True, ondelete="restrict"
    )

    @api.model
    def _hv_order_target(self, order):
        amount = round(order._fix_amount_due(), 2)
        return order, amount, True

    @api.model
    def _hv_target_from_vals(self, vals):
        order = self.env["fix.service.order"].browse(vals.get("order_id")).exists()
        if order:
            if vals.get("sale_id") or vals.get("basket_id"):
                raise UserError("Choose the service order, the counter sale or the basket: one.")
            return self._hv_order_target(order)
        return super()._hv_target_from_vals(vals)

    @api.model
    def _hv_is_open(self, record):
        if record._name == "fix.service.order":
            return record.payment_settlement_state == "unpaid" and record.state not in (
                "closed",
                "cancelled",
            )
        return super()._hv_is_open(record)

    @api.model
    def _hv_check_for(self, record):
        if record._name == "fix.service.order":
            return self.sudo().search([("order_id", "=", record.id)], limit=1)
        return super()._hv_check_for(record)

    @api.model
    def _hv_link_vals(self, record):
        if record._name == "fix.service.order":
            return {"order_id": record.id, "sale_id": False}
        return super()._hv_link_vals(record)
