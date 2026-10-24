# Withholding-certificate report parsers (P07-M04 T04, DT-013).
#
# The two statutory certificates printed from fix.withholding.certificate:
#   * Mushak 6.6 — VAT deducted at source (VAT & SD Rules 2016, rule 40)
#   * the income-tax withholding certificate (Income Tax Act 2023, s.52)
# The parsers enforce what may be certified (DT-013 FM-13-a/b: only an
# ISSUED certificate of the right type, and never without the treasury
# deposit it certifies) and hand the template backend-formatted BN-007
# amounts and the amount in words — the template only places them.
from odoo import api, models
from odoo.exceptions import UserError

from .statutory_format import amount_in_words, bn_numerals, format_bdt, format_rate


class _WithholdingCertificateReport(models.AbstractModel):
    _name = "report.cd_tax_engine_bd.withholding_base"
    _description = "Withholding certificate report base"

    _certificate_type = ""
    _form_label = ""

    @api.model
    def _supply(self, cert) -> dict:
        """The certified supply from the AP invoice (cd_ap_ext's pointer)."""
        invoice = cert["vendor_invoice_id"] if "vendor_invoice_id" in cert._fields else None
        return {
            "ref": invoice.invoice_ref if invoice else "",
            "date": invoice.invoice_date if invoice else False,
            "description": ", ".join(invoice.line_ids.mapped("description")) if invoice else "",
        }

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env["fix.withholding.certificate"].browse(docids)
        problems = []
        for cert in docs:
            ref = cert.certificate_no or "draft #%s" % cert.id
            if cert.certificate_type != self._certificate_type:
                problems.append("%s is of another certificate type" % ref)
            elif cert.state != "issued":
                problems.append("%s is not issued" % ref)
            elif not cert.challan_no:
                problems.append("%s has no treasury deposit (challan) reference" % ref)
        if problems:
            raise UserError("%s cannot be printed: %s" % (self._form_label, "; ".join(problems)))
        return {
            "doc_ids": docs.ids,
            "doc_model": "fix.withholding.certificate",
            "docs": docs,
            "supply": {cert.id: self._supply(cert) for cert in docs},
            "fmt_bdt": format_bdt,
            "fmt_rate": format_rate,
            "in_words": amount_in_words,
            "bn": bn_numerals,
        }


class ReportMushak66(models.AbstractModel):
    _name = "report.cd_tax_engine_bd.report_mushak66"
    _inherit = "report.cd_tax_engine_bd.withholding_base"
    _description = "Mushak 6.6 VDS certificate"

    _certificate_type = "mushak_6_6"
    _form_label = "Mushak 6.6"


class ReportWithholdingCertificate(models.AbstractModel):
    _name = "report.cd_tax_engine_bd.report_withholding_certificate"
    _inherit = "report.cd_tax_engine_bd.withholding_base"
    _description = "Income-tax withholding certificate (ITA 2023 s.52)"

    _certificate_type = "section_52_income_tax"
    _form_label = "Income-tax withholding certificate"
