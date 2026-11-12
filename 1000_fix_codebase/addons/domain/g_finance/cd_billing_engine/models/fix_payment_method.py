# M20: the ONE list of ways a customer can pay (quote-to-cash review P1,
# 12 Nov 2026).
#
# Before this, each document kept its own hard-coded list: field service
# (cash/bkash/nagad), the front desk (cash/bkash/nagad/card), the AR receipt
# (RECEIPT_METHODS, nine values), treasury ("mobile_fs"), subscriptions,
# the storefront. Rocket and Upay existed nowhere, and a quotation could not
# say how the customer may pay. This master is what quotations offer today;
# each method names the AR receipt tender it is booked as (receipt_method),
# so receipts, the counter and field collection can move onto it without a
# second mapping.
from odoo import api, fields, models
from odoo.exceptions import ValidationError

from .fix_ar_engine import RECEIPT_METHODS

METHOD_TYPES = [
    ("cash", "Cash"),
    ("cheque", "Cheque / Pay Order"),
    ("bank_transfer", "Bank Transfer (BEFTN / RTGS / NPSB)"),
    ("mfs", "Mobile Financial Service"),
    ("card", "Card / Online Gateway"),
    ("cod", "Cash on Delivery"),
    ("on_account", "On Account (credit terms)"),
]

# The journals a method settles through on this estate, by journal code
# (fix_real, 12 Nov 2026). Linked once on install where the journal exists;
# Finance maintains them afterwards. Rocket and Upay have no journal yet.
DEFAULT_JOURNAL_CODES = {
    "BKASH": "BKASH",
    "NAGAD": "NAGAD",
    "CHEQUE": "CIH",
}


class FixPaymentMethod(models.Model):
    _name = "fix.payment.method"
    _description = "Customer Payment Method"
    _order = "sequence, id"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True, help="Stable key, e.g. BKASH, ROCKET, BEFTN.")
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    method_type = fields.Selection(METHOD_TYPES, required=True)
    receipt_method = fields.Selection(
        RECEIPT_METHODS,
        string="Booked As (AR receipt tender)",
        help="The fix.ar.receipt method a payment by this means is recorded with.",
    )
    journal_id = fields.Many2one(
        "account.journal",
        string="Settles Through",
        domain="[('type', 'in', ('bank', 'cash'))]",
        help="The bank / cash / wallet journal the money lands in. Finance maintains it.",
    )
    fee_pct = fields.Float(string="Collection Fee (%)", help="MFS / card charge, if any.")
    settlement_days = fields.Integer(help="Days until the money reaches the bank.")
    for_counter = fields.Boolean(string="Counter / Front Desk", default=True)
    for_field = fields.Boolean(string="Field Collection", default=True)
    for_portal = fields.Boolean(string="Online / Portal", default=False)
    for_corporate = fields.Boolean(string="Corporate & Tender", default=False)
    note = fields.Char(help="What the customer is told, e.g. the merchant number.")

    _code_unique = models.Constraint("UNIQUE(code)", "A payment method code is unique.")

    @api.constrains("fee_pct", "settlement_days")
    def _check_numbers(self):
        for rec in self:
            if not 0.0 <= (rec.fee_pct or 0.0) <= 100.0:
                raise ValidationError("A collection fee is between 0 and 100%.")
            if (rec.settlement_days or 0) < 0:
                raise ValidationError("Settlement days cannot be negative.")

    @api.model
    def _link_default_journals(self):
        """Install hook: point the seeded methods at the estate's journals
        where they exist. Never overwrites a journal Finance has set."""
        Journal = self.env["account.journal"].sudo()
        for code, journal_code in DEFAULT_JOURNAL_CODES.items():
            method = self.sudo().with_context(active_test=False).search([("code", "=", code)])
            if not method or method.journal_id:
                continue
            journal = Journal.search(
                [("code", "=", journal_code), ("type", "in", ("bank", "cash"))], limit=1
            )
            if journal:
                method.journal_id = journal
        return True
