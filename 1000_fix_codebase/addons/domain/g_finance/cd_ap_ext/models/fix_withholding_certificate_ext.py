# fix.withholding.certificate AP extension (P07-M04, T05 certificates) —
# the vendor-invoice pointer. cd_tax_engine_bd owns the certificate model but
# sits BELOW cd_ap_ext in the module graph (cd_ap_ext depends on the tax
# engine for VAT determination); the pointer to M52's invoice therefore lives
# here, on the AP side of the boundary (dependency-cycle finding).
#
# A08 build: a certificate may cover a non-AP payment (A05 trade-in payouts
# carry source_model / source_ref), so the bill is required only when the
# certificate is an AP one (source_model empty or fix.vendor.invoice).
from odoo import api, fields, models
from odoo.exceptions import ValidationError

AP_SOURCES = (False, "", "fix.vendor.invoice")


class FixWithholdingCertificateApExt(models.Model):
    _inherit = "fix.withholding.certificate"

    vendor_invoice_id = fields.Many2one(
        "fix.vendor.invoice", string="Vendor Invoice", required=False, ondelete="cascade"
    )

    @api.constrains("vendor_invoice_id", "source_model")
    def _check_vendor_invoice(self):
        for cert in self:
            if (cert.source_model or False) in AP_SOURCES and not cert.vendor_invoice_id:
                raise ValidationError(
                    "An AP withholding certificate names the vendor bill it covers; a "
                    "certificate for another payment names its source model."
                )
