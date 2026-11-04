# fix_bi_export_log — M25 (A11 audit E6 / BRU-BID-11): every pack export is
# logged — who, what, which scope, how many rows. The log is APPEND-ONLY:
# no edit, no delete, not even for admin, exactly like the M62 purge
# evidence. If a number left the building, the record of it cannot change.
from odoo import fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class FixBiExportLog(models.Model):
    """One row per pack export (screen download or scheduled distribution)."""

    _name = "fix.bi.export.log"
    _description = "BI Export Log"
    _order = "ran_at desc, id desc"

    ran_at = fields.Datetime(default=fields.Datetime.now, required=True, index=True)
    user_id = fields.Many2one(
        "res.users", string="Exported By", required=True, index=True, ondelete="restrict"
    )
    pack = fields.Char(required=True, index=True, help="module:report, e.g. M25:finance_pack")
    channel = fields.Selection(
        [("download", "Screen Download"), ("distribution", "Scheduled Distribution")],
        required=True,
        default="download",
    )
    format = fields.Char(help="csv / xlsx / json")
    company_ids = fields.Char(
        string="Scope (companies)", help="Comma-separated company names the export covered."
    )
    row_count = fields.Integer()
    params_json = fields.Text(string="Parameters (JSON)")

    def write(self, vals):
        raise UserError(_("An export log row is append-only (BRU-BID-11) — it cannot be edited."))

    def unlink(self):
        raise UserError(_("An export log row is append-only (BRU-BID-11) — it cannot be deleted."))
