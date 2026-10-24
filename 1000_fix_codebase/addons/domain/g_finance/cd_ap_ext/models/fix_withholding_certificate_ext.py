# fix.withholding.certificate AP extension (P07-M04, T05 certificates) —
# the vendor-invoice pointer. cd_tax_engine_bd owns the certificate model but
# sits BELOW cd_ap_ext in the module graph (cd_ap_ext depends on the tax
# engine for VAT determination); the pointer to M52's invoice therefore lives
# here, on the AP side of the boundary (dependency-cycle finding).
from odoo import fields, models


class FixWithholdingCertificateApExt(models.Model):
    _inherit = "fix.withholding.certificate"

    vendor_invoice_id = fields.Many2one(
        "fix.vendor.invoice", string="Vendor Invoice", required=True, ondelete="cascade"
    )
