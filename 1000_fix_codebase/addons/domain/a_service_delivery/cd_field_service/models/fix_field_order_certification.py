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
#
# A09 round 2: a certification can lapse, be suspended or be revoked AFTER the
# dispatch. Starting the work re-checks eligibility and refuses it, and the
# certification.expired / .suspended / .revoked consumer (cd_competency) calls
# _fix_flag_certification_lost here to give a dispatcher one to-do per
# not-started order. No field-service state is changed by either.
from odoo import models
from odoo.exceptions import UserError

# Orders assigned to a technician on which the work has not started.
NOT_STARTED = ("draft", "pending_dispatch", "dispatched", "accepted", "en_route", "arrived")
DISPATCHER = "cd_field_service.group_fix_field_service_manager"


class FixFieldOrderCertification(models.Model):
    _inherit = "fix.field.order"

    def _fix_certification_problem(self, technician=None):
        """Why the technician may not take this order (None when they may)."""
        self.ensure_one()
        tech = technician or self.technician_id
        if not tech:
            return None
        if self.env["fix.certification.waiver"]._fix_covers("fix.field.order", self.id, tech):
            return None
        device = self.sudo().order_id.device_id
        device_type = device.device_type or None if device else None
        brand = device.device_model_id.brand_id if device and device.device_model_id else None
        eligible, reason = self.env["fix.certification"].dispatch_eligibility(
            tech,
            device_type=device_type,
            brand_id=brand,
            fail_closed=True,
            requires_vehicle=self._fix_travels_by_vehicle(tech),
        )
        return None if eligible else reason

    def _fix_travels_by_vehicle(self, technician):
        """FR-HSE-019: the order travels by vehicle when it carries the
        technician's van (van_location_id, set at dispatch from the
        technician's van stock location, which is what dispatch is about to
        set), or when M46 assigned a vehicle to this technician for the
        service order (fix.vehicle.assignment, when cd_vehicle_ext is
        installed)."""
        self.ensure_one()
        rec = self.sudo()
        if rec.van_location_id and rec.van_location_id.technician_id == technician:
            return True
        if rec.env["fix.stock.location"].search_count(
            [
                ("technician_id", "=", technician.id),
                ("is_van_stock", "=", True),
                ("state", "!=", "inactive"),
            ]
        ):
            return True
        if "fix.vehicle.assignment" in rec.env and rec.order_id:
            return bool(
                rec.env["fix.vehicle.assignment"].search_count(
                    [("order_id", "=", rec.order_id.id), ("technician_id", "=", technician.id)]
                )
            )
        return False

    def _fix_assert_certified(self, technician=None):
        for rec in self:
            reason = rec._fix_certification_problem(technician)
            if reason:
                raise UserError("M22 eligibility: dispatch of %s blocked — %s" % (rec.name, reason))
        return True

    def _fix_not_started_states(self):
        return NOT_STARTED

    def _fix_flag_certification_lost(self, certification, event_type):
        """Consumer side (certification.expired / .suspended / .revoked): one
        dispatcher to-do per not-started order whose technician no longer
        qualifies. The order is not changed."""
        flagged = self.browse()
        group = self.env.ref(DISPATCHER, raise_if_not_found=False)
        for rec in self.sudo():
            if rec.state not in NOT_STARTED or not rec.technician_id:
                continue
            reason = rec._fix_certification_problem()
            if not reason:
                continue
            dispatchers = (
                group.sudo()
                .all_user_ids.filtered(
                    lambda u, c=rec.company_id: u.active and not u.share and c in u.company_ids
                )
                .sorted("id")
                if group
                else self.env["res.users"]
            )
            user = dispatchers[:1] or rec.create_uid
            summary = "Reassign %s: certification %s" % (rec.name, event_type.split(".")[-1])
            Activity = self.env["mail.activity"].sudo()
            if Activity.search_count(
                [
                    ("res_model", "=", rec._name),
                    ("res_id", "=", rec.id),
                    ("user_id", "=", user.id),
                    ("summary", "=", summary),
                ]
            ):
                continue
            rec.activity_schedule(
                "mail.mail_activity_data_todo",
                summary=summary,
                note="%s (%s) no longer qualifies for this order: %s. Reassign it or request "
                "a certification waiver before work starts."
                % (rec.technician_id.name, certification.display_name, reason),
                user_id=user.id,
            )
            flagged |= rec
        return flagged

    def action_start_work(self):
        """The technician starts work only while still eligible: a
        certification that lapsed, was suspended or was revoked after the
        dispatch stops it here (FR-LMS-013, BRU-LMS-03)."""
        for rec in self:
            reason = rec._fix_certification_problem()
            if reason:
                raise UserError(
                    "M22 eligibility: work on %s cannot start — %s" % (rec.name, reason)
                )
        return super().action_start_work()

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
