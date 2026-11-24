# fix.disposal.record — the permanent disposal register (A10 D2, M24-7).
#
# Before this register a document could be deleted from inside its retention
# window with nothing left behind but a chatter row; "state=destroyed" was a
# free write with the file still stored. Disposal now happens only through
# fix.document.action_dispose, which files this record and a destruction
# certificate and wipes the file.
from odoo import fields, models
from odoo.exceptions import UserError


class FixDisposalRecord(models.Model):
    """The permanent record that a document was destroyed."""

    _name = "fix.disposal.record"
    _description = "Disposal Record"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(required=True)
    document_id = fields.Many2one("fix.document", required=True, ondelete="restrict", index=True)
    method = fields.Selection(
        [
            ("secure_wipe", "Secure Wipe"),
            ("physical_shredding", "Physical Shredding"),
            ("degaussing", "Degaussing"),
        ],
        default="secure_wipe",
        required=True,
    )
    disposed_on = fields.Date(default=lambda self: fields.Date.context_today(self), required=True)
    performed_by_id = fields.Many2one("res.users", required=True, readonly=True)
    certificate_doc_id = fields.Many2one(
        "fix.document", string="Destruction Certificate", readonly=True, ondelete="restrict"
    )
    # A10 deep audit (2026-11-22, A2-F04): the fingerprint of WHAT was wiped,
    # sealed on the register before the bytes go — the surviving document row
    # recomputes its checksum to False after the wipe, so without this the
    # system could not prove which payload a disposal destroyed.
    payload_sha256 = fields.Char(
        readonly=True,
        help="The sha256 of the destroyed bytes, sealed at disposal time.",
    )
    payload_size = fields.Integer(
        readonly=True,
        help="The byte count of the destroyed payload, sealed at disposal time.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "document_id",
            "method",
            "disposed_on",
            "performed_by_id",
            "certificate_doc_id",
            "payload_sha256",
            "payload_size",
        }

    def unlink(self):
        # The register is permanent: an entry leaves only with its document
        # (cascade at the database level never happens — ondelete=restrict).
        if not self.env.su:
            raise UserError(
                "The disposal register is permanent: a destruction record is never deleted."
            )
        return super().unlink()
