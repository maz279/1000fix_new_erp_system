# ir.attachment extension — route fix.document attachments to the object store.
from odoo import fields, models


class IrAttachmentExt(models.Model):
    """Extend ir.attachment with document-kernel awareness.

    The extension does NOT change storage (Odoo already routes attachments
    to the configured storage backend); it adds the residency classification
    flag so the FF-09 check can verify that classified attachments are
    routed correctly.
    """
    _inherit = "ir.attachment"

    # Set by fix.document when a document is residency-classified
    is_residency_classified = fields.Boolean(
        default=False,
        help="True if this attachment contains residency-classified data. "
             "If True, the attachment must be stored in Z4 (FF-09).")
