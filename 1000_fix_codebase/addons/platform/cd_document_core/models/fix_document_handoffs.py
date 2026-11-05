# A12 audit (2026-11-04) D8 hand-off "M66 assets -> M06 data destruction":
# an ITSM asset could be retired with its governed documents (warranty
# cards, asset documents, identity documents) still live under the old
# retention clock. cd_itsm publishes itsm.asset_retired; this consumer
# stamps every document linked to the retired asset so the destruction
# review the retention class demands is visible on the document itself.
from odoo import models


class FixDocumentItsmHandoff(models.Model):
    _inherit = "fix.document"

    def consume_itsm_asset_retired(self, event):
        """Chatter-flag documents linked to a retired ITSM asset.

        Idempotent: the note body carries the event id; a redelivery finds
        it on the last message and does not re-post.
        """
        payload = event.get("payload") or {}
        asset_id = payload.get("asset_id") or payload.get("id")
        if not asset_id:
            return 0
        asset_label = payload.get("asset_tag") or payload.get("name") or str(asset_id)
        event_id = event.get("event_id") or ""
        docs = self.sudo().search(
            [("res_model", "=", "fix.itsm.asset"), ("res_id", "=", int(asset_id))]
        )
        posted = 0
        for doc in docs:
            body = (
                "Asset %s retired — data destruction review due per retention class %s (event %s)."
                % (
                    asset_label,
                    doc.retention_class_id.name or "unclassified",
                    event_id,
                )
            )
            if event_id and any(event_id in (m.body or "") for m in doc.message_ids):
                continue
            doc.message_post(body=body)
            posted += 1
        return posted
