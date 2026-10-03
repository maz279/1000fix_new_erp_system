# fix.document.template — M24 completion (P06-M08-T01, CD-M24-05).
# The template engine's data side: which template generates which document
# type, in which language, with which QWeb report reference. Generation
# itself runs through services/document-generation (the W3 engine).
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FixDocumentTemplate(models.Model):
    _name = "fix.document.template"
    _description = "Document Template"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _code_unique = models.Constraint('UNIQUE (code)', 'Template code must be unique')

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    code = fields.Char(required=True, size=32)
    name = fields.Char(required=True)
    name_bn = fields.Char(string="Name (Bengali)", help="DE-17")
    document_type = fields.Selection(
        [("service_report", "Service Report"), ("evidence_pack", "Evidence Pack"),
         ("invoice", "Invoice"), ("receipt", "Receipt"), ("contract", "Contract"),
         ("notice", "Statutory Notice")],
        required=True)
    report_ref = fields.Char(
        string="QWeb Report XML ID",
        help="e.g. cd_tax_engine_bd.report_mushak63 — the rendering entry point")
    bilingual = fields.Boolean(
        default=True,
        help="Every template ships Bengali and English variants (AS-12)")
    requires_approval = fields.Boolean(
        default=False,
        help="Documents from this template enter the approval chain before issue")

    @api.constrains("bilingual", "name_bn")
    def _check_bilingual(self):
        for template in self:
            if template.bilingual and not template.name_bn:
                raise ValidationError(
                    "A bilingual template needs its Bengali name (AS-12)")
