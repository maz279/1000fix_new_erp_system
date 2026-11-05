# ir.attachment extension — route fix.document attachments to the object store.
#
# A10 D2 (2026-11-05, findings M24-3/-9): the audit swapped a SIGNED
# document's file by writing ir.attachment.datas directly — the document's
# own field freeze never saw it, and the completed envelope kept its old
# hash over the new bytes. An attachment bound to a held or signature-locked
# document is frozen at the source: the file a hold or a signature covers
# can no longer be swapped, renamed or deleted underneath the record.
from odoo import fields, models
from odoo.exceptions import UserError

# ir.attachment fields that carry the file's identity; anything else
# (res_model, mimetype) stays serviceable.
_FILE_FIELDS = {"datas", "name", "raw", "db_datas"}


class IrAttachmentExt(models.Model):
    """Extend ir.attachment with document-kernel awareness."""

    _inherit = "ir.attachment"

    # Set by fix.document when a document is residency-classified
    is_residency_classified = fields.Boolean(
        default=False,
        help="True if this attachment contains residency-classified data. "
        "If True, the attachment must be stored in Z4 (FF-09).",
    )

    def _sealed_documents(self):
        return self.env["fix.document"].sudo().search_count(
            [
                ("attachment_id", "in", self.ids),
                "|",
                ("legal_hold", "=", True),
                ("signature_locked", "=", True),
            ]
        )

    def write(self, vals):
        if self and _FILE_FIELDS & set(vals) and not self.env.su and self._sealed_documents():
            raise UserError(
                "This file is under a legal hold or an e-signature seal: its bytes "
                "are evidence and cannot be changed. Release the hold or void the "
                "envelope first (A10 D2 / M24-3)."
            )
        return super().write(vals)

    def unlink(self):
        if self and not self.env.su and self._sealed_documents():
            raise UserError(
                "This file is under a legal hold or an e-signature seal: its bytes "
                "are evidence and cannot be deleted. Release the hold or void the "
                "envelope first (A10 D2 / M24-3)."
            )
        return super().unlink()
