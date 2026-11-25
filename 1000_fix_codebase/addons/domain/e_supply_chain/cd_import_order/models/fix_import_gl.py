# fix_import_gl — M44 as a posting source in M19's posting log.
from odoo import fields, models


class FixJournalPostingLogImport(models.Model):
    _inherit = "fix.journal.posting.log"

    source = fields.Selection(
        selection_add=[("import_subledger", "Import & Landed Cost (M44)")],
        ondelete={"import_subledger": lambda recs: recs.write({"source": "api"})},
    )
