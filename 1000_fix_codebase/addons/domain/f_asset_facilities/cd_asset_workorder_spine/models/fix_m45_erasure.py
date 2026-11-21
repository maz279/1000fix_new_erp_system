# fix_m45_erasure — A07 ERP audit (2026-11-20) M45-21 (AUT-EAM-15, BRU-EAM-16,
# AC-16): a data-bearing item left the company on a TYPED erasure reference.
# Now its approved retirement raises the M06 secure-erasure request, and the
# disposal waits until M06 has certified the erasure (a verified wipe
# certificate); the certificate's number is what the retirement records.
from odoo import fields, models
from odoo.exceptions import UserError

ROUTE_DISPOSITION = {
    "resale": "resale",
    "ewaste": "recycling",
    "scrap": "recycling",
    "return_supplier": "recycling",
}


class FixEquipmentRetirementErasure(models.Model):
    _inherit = "fix.equipment.retirement"

    wipe_request_id = fields.Many2one(
        "fix.data.wipe.request",
        string="M06 Erasure Request",
        readonly=True,
        copy=False,
        ondelete="restrict",
    )
    wipe_state = fields.Selection(related="wipe_request_id.state", string="Erasure Status")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"wipe_request_id"}

    def write(self, vals):
        result = super().write(vals)
        if vals.get("state") == "approved":
            self._m45_raise_erasure()
        return result

    def _m45_raise_erasure(self):
        Request = self.env["fix.data.wipe.request"].sudo()
        for rec in self.sudo():
            if not rec.data_bearing or rec.wipe_request_id:
                continue
            equipment = rec.equipment_id
            request = Request.create(
                {
                    "company_id": rec.company_id.id or self.env.company.id,
                    "operating_unit_id": rec.operating_unit_id.id or False,
                    "source": "corporate_decommission",
                    "source_ref": "%s / %s" % (rec.name, equipment.code),
                    "serial_number": equipment.serial_no or equipment.asset_tag or equipment.code,
                    "media_description": " ".join(
                        part for part in (equipment.manufacturer, equipment.model_name) if part
                    )
                    or equipment.name,
                    "confidentiality_level": "high",
                    "disposition": ROUTE_DISPOSITION.get(rec.disposal_route, "recycling"),
                    "notes": "Retired company equipment %s (%s): erase before it leaves "
                    "(BRU-EAM-16)." % (equipment.name, rec.name),
                }
            )
            rec._guarded().write({"wipe_request_id": request.id})
            rec.message_post(
                body="M06 erasure request %s raised: the item is disposed of only once its "
                "erasure is certified." % request.name
            )

    def action_dispose(self):
        for rec in self:
            # not approved yet: the retirement's own refusal says so first
            if not rec.data_bearing or rec.state != "approved":
                continue
            request = rec.sudo().wipe_request_id
            if not request:
                rec._m45_raise_erasure()
                request = rec.sudo().wipe_request_id
            if request.state != "certified":
                raise UserError(
                    "%s holds data: M06 has not certified its erasure yet (request %s is %s). "
                    "It may not leave the company before (BRU-EAM-16)."
                    % (
                        rec.equipment_id.name,
                        request.name,
                        dict(request._fields["state"].selection).get(request.state, "-"),
                    )
                )
            cert = request.certificate_ids.filtered(
                lambda c: c.sanitization_status == "verified"
            ).sorted("id")[-1:]
            if cert and (rec.erasure_certificate_ref or "").strip() != cert.name:
                rec.write({"erasure_certificate_ref": cert.name})
        return super().action_dispose()
