# cd_field_service — the M22 certification gate on home-service dispatch
# (A09 workflow audit M22-F1, report C4; FR-LMS-039, BRU-LMS-01/02, AC-01).
#
# fix.field.order.action_dispatch / action_reassign never called
# dispatch_eligibility: certification only added +25 to a suggestion score,
# and a dispatcher sent a technician with no certification to a customer's
# home. Both transitions now refuse a technician who does not hold a valid
# certification for the job's device (and brand), failing CLOSED for a device
# type no gating competency covers. The only way past is an approved
# fix.certification.waiver naming this technician on this order.
#
# This file is owned by the A09 M22 work (cd_competency); technician_id is a
# guarded field on the field order, so these two transitions are the only
# paths that assign a technician.
from odoo import models
from odoo.exceptions import UserError


class FixFieldOrderCertification(models.Model):
    _inherit = "fix.field.order"

    def _fix_assert_certified(self, technician=None):
        Cert = self.env["fix.certification"]
        Waiver = self.env["fix.certification.waiver"]
        for rec in self:
            tech = technician or rec.technician_id
            if not tech:
                continue
            if Waiver._fix_covers("fix.field.order", rec.id, tech):
                continue
            device = rec.order_id.device_id
            device_type = device.device_type or None if device else None
            brand = device.device_model_id.brand_id if device and device.device_model_id else None
            eligible, reason = Cert.dispatch_eligibility(
                tech, device_type=device_type, brand_id=brand, fail_closed=True
            )
            if not eligible:
                raise UserError("M22 eligibility: dispatch of %s blocked — %s" % (rec.name, reason))
        return True

    def action_dispatch(self, technician_id=None):
        self._fix_require_dispatcher("Dispatching a field order")
        self._fix_assert_certified(self._fix_resolve_technician(technician_id))
        return super().action_dispatch(technician_id=technician_id)

    def action_reassign(self, technician_id=None, reason="", reassignment=None):
        self._fix_require_dispatcher("Reassigning a field order")
        target = technician_id
        if reassignment not in (None, "", False):
            target = str(reassignment).strip().partition(" ")[0]
        if target:
            technician = self._fix_resolve_technician(target)
            if technician:
                self._fix_assert_certified(technician)
        return super().action_reassign(
            technician_id=technician_id, reason=reason, reassignment=reassignment
        )

    def action_request_certification_waiver(self, technician_id=None, reason=None, waiver=None):
        """A dispatcher asks the Certification Override Approver to let one
        uncertified technician take this order (BRU-LMS-02, FR-LMS-040).
        ``waiver`` is the workspace prompt's one string: "<employee id> <reason>".
        The dispatcher who asks never decides it."""
        self.ensure_one()
        self._fix_require_dispatcher("Requesting a certification waiver")
        if waiver not in (None, "", False):
            head, _sep, tail = str(waiver).strip().partition(" ")
            technician_id, reason = head, tail
        technician = self._fix_resolve_technician(technician_id) or self.technician_id
        req = self.env["fix.certification.waiver"]._fix_request_for(
            "fix.field.order", self.id, technician, reason
        )
        return {"waiver_id": req.id}
