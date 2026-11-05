# M09 consumer of the knowledge recall routing (A10 P1-7, M61-4).
#
# When M61 distributes a safety recall bulletin (event `bulletin.distributed`,
# payload bulletin_type == "recall"), the warranty side OWNS the campaign: a
# fix.warranty.recall record is created (or refreshed) from the bulletin's
# own scope — affected models, serial range, brand, severity — and goes
# active. The consumer runs only from the event relay (superuser), is
# idempotent on bulletin_id, and never invents a unit count the bulletin did
# not state: affected_units stays 0 until the campaign's own numbers arrive.
from odoo import api, fields, models
from odoo.exceptions import AccessError


class FixWarrantyRecallBulletinConsumer(models.Model):
    _inherit = "fix.warranty.recall"

    @api.model
    def consume_bulletin_distributed(self, event):
        if not self.env.su:
            raise AccessError("Warranty recall consumers run only from the event relay.")
        payload = event.get("payload") or {}
        if payload.get("bulletin_type") != "recall":
            return True  # M09 owns recall campaigns, not every bulletin
        try:
            bulletin_id = int(event.get("aggregate_id") or 0)
        except (TypeError, ValueError):
            bulletin_id = 0
        if not bulletin_id:
            return True
        bulletin = self.env["fix.knowledge.bulletin"].browse(bulletin_id).exists()
        if not bulletin:
            return True  # the bulletin left before the relay ran; nothing to build
        models_txt = ", ".join(
            m.strip() for m in (payload.get("affected_models") or "").split(",") if m.strip()
        )
        serials = (payload.get("serial_scope") or "").strip()
        product_ref = " / ".join(x for x in (models_txt, serials) if x) or "—"
        brand = self.env["fix.brand"].search([("name", "=", payload.get("brand"))], limit=1)
        note = "From bulletin %s (%s severity; %d recipient branch(es))%s" % (
            payload.get("name") or bulletin.name,
            payload.get("severity") or bulletin.severity,
            len(payload.get("recipients") or []),
            "; serials: %s" % serials if serials else "",
        )
        campaign = self.search([("bulletin_id", "=", bulletin_id)], limit=1)
        if campaign:
            # A re-distribution refreshes the campaign's scope; a campaign the
            # warranty desk already completed or cancelled is theirs.
            campaign.write({"product_ref": product_ref, "note": note})
            campaign.message_post(
                body="Refreshed from bulletin %s by the event relay." % bulletin.name
            )
            return True
        campaign = self.create(
            {
                "name": payload.get("name") or bulletin.name,
                "brand_id": brand.id,
                "product_ref": product_ref,
                # honest by construction: the bulletin states models and
                # serials, not a unit count — the campaign counts its own units
                # as claims arrive (A10 P1-7).
                "affected_units": 0,
                "launched_on": fields.Date.context_today(self),
                "state": "active",
                "note": note,
                "bulletin_id": bulletin_id,
            }
        )
        campaign.message_post(
            body="Recall campaign opened from bulletin %s distributed by %s."
            % (bulletin.name, payload.get("severity") or "the publisher")
        )
        bulletin.sudo().message_post(
            body="M09 recall campaign '%s' is active (A10 P1-7)." % campaign.name
        )
        return True
