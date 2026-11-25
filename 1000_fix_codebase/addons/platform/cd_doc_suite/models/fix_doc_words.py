"""amount-in-words computed fields for every documented model.

Rule 40, VAT & SD Rules 2016 (and standard BD commercial practice per the
legacy TFSL/SI/RT-006 invoice): amounts must print in figures AND in words.
The wording comes from cd_tax_engine_bd.statutory_format.amount_in_words()
(lakh-crore, "Taka ... Only") — the same certified wording the statutory
Mushak 6.6 / TDS certificates already print, so no second implementation
can drift from the first (DRY; AS-10 report layer reads, never computes).
"""

from odoo import fields, models
from odoo.addons.cd_tax_engine_bd.models.statutory_format import amount_in_words


def _safe_words(amount) -> str:
    """Never break a document print over wording: empty string on bad input."""
    try:
        return amount_in_words(amount)
    except Exception:
        return ""


class FixQuotation(models.Model):
    _inherit = "fix.quotation"

    amount_in_words_en = fields.Char(
        compute="_compute_amount_in_words_en",
        string="Amount in Words",
        help="Total payable (value + VAT) in words, lakh-crore wording.",
    )

    def _compute_amount_in_words_en(self):
        for rec in self:
            rec.amount_in_words_en = _safe_words(rec.amount_total)


class FixEstimate(models.Model):
    _inherit = "fix.estimate"

    amount_in_words_en = fields.Char(
        compute="_compute_amount_in_words_en",
        string="Amount in Words",
    )

    def _compute_amount_in_words_en(self):
        for rec in self:
            rec.amount_in_words_en = _safe_words(rec.grand_total)


class FixArInvoice(models.Model):
    _inherit = "fix.ar.invoice"

    amount_in_words_en = fields.Char(
        compute="_compute_amount_in_words_en",
        string="Amount in Words",
    )

    def _compute_amount_in_words_en(self):
        for rec in self:
            rec.amount_in_words_en = _safe_words(rec.total_payable)


class FixMushakRegister(models.Model):
    _inherit = "fix.mushak.register"

    amount_in_words_en = fields.Char(
        compute="_compute_amount_in_words_en",
        string="Amount in Words",
    )

    def _compute_amount_in_words_en(self):
        for rec in self:
            rec.amount_in_words_en = _safe_words(rec.total_payable)


class FixArReceipt(models.Model):
    _inherit = "fix.ar.receipt"

    amount_in_words_en = fields.Char(
        compute="_compute_amount_in_words_en",
        string="Amount in Words",
    )

    def _compute_amount_in_words_en(self):
        for rec in self:
            rec.amount_in_words_en = _safe_words(rec.amount)


class FixPurchaseOrder(models.Model):
    _inherit = "fix.purchase.order"

    amount_in_words_en = fields.Char(
        compute="_compute_amount_in_words_en",
        string="Amount in Words",
    )

    def _compute_amount_in_words_en(self):
        for rec in self:
            rec.amount_in_words_en = _safe_words(rec.amount_total)


class FixVendorInvoice(models.Model):
    _inherit = "fix.vendor.invoice"

    amount_in_words_en = fields.Char(
        compute="_compute_amount_in_words_en",
        string="Amount in Words",
    )

    def _compute_amount_in_words_en(self):
        for rec in self:
            rec.amount_in_words_en = _safe_words(rec.total_payable)
