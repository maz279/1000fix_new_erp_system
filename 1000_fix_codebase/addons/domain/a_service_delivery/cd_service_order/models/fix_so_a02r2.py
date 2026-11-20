# A02 ERP audit, pass 2 (20 Nov 2026): the M01 service-order actions and
# crons the second audit found missing, and the contracts other streams call.
#
#  - M01-02 / M01-07 / M01-15: who the order is for, which device, its LCI
#    finding and its branch are fixed after intake (fix_service_order write);
#    a Service Supervisor corrects them here, with a reason, and the
#    approvals and codes bound to them are voided.
#  - M01-05: delivered orders close by cron once the close gate passes.
#  - M01-13 (D13): uncollected-device reminders, the formal notice and the
#    disposal period.
#  - D4: an on-site job completed in the field (sign-off + post-work photo)
#    is delivered there: action_complete_onsite (called by M02's hand-back).
#  - X5-16: an approved estimate reserves its parts in M15.
#
# Imported after fix_so_settlement_ext (it reads the settlement rules).
import logging

from odoo import api, fields, models
from odoo.addons.cd_catalogue.models.fix_commercial_line import STOCK_LINE_TYPES
from odoo.exceptions import UserError

from .fix_service_order import GROUP_SUPERVISOR

logger = logging.getLogger(__name__)

# D4: the token that lets an on-site completion move the order straight to
# Delivered (the field sign-off is the QC and the handover).
_ONSITE_KEY = "fix_so_onsite_completion"
_ONSITE_TOKEN = object()
_ONSITE_FROM = ("approved", "in_repair", "qc_pending", "qc_failed", "ready")
# who, besides the event relay (superuser), completes an on-site job here
_ONSITE_GROUPS = (GROUP_SUPERVISOR, "cd_field_service.group_fix_field_service_manager")
_FIELD_EVIDENCE_PROFILE_PARAM = "cd_field_service.completion_evidence_profile"
# corrections are made before the customer has the price (M01-02)
_CORRECTABLE_STATES = ("draft", "intake", "diagnostic", "estimate_pending")


class FixServiceOrderPass2(models.Model):
    _inherit = "fix.service.order"

    # ------------------------------------------------------------ helpers
    def _validate_transition(self, new_state: str) -> None:
        if (
            new_state == "delivered"
            and self.env.context.get(_ONSITE_KEY) is _ONSITE_TOKEN
            and self.state in _ONSITE_FROM
        ):
            # D4: the field sign-off, post-work photo and field payment were
            # checked by action_complete_onsite; the depot QC and the counter
            # handover gates do not apply to a device that never left the site
            return
        return super()._validate_transition(new_state)

    def _fix_assert_supervisor_reason(self, what, reason) -> str:
        self._fix_assert_supervisor(what)
        reason = (reason or "").strip()
        if not reason:
            raise UserError("Give the reason for this correction (%s)." % what.lower())
        return reason

    @staticmethod
    def _fix_id(value):
        if hasattr(value, "id"):
            return value.id
        if isinstance(value, list | tuple):
            value = value[0] if value else False
        try:
            return int(value) if value else False
        except (TypeError, ValueError):
            raise UserError("Not a record id: %r" % (value,)) from None

    # ------------------------------------------------ M01-02: customer / device
    def action_correct_customer_device(self, customer_id=None, device_id=None, reason=None):
        """A Service Supervisor corrects the customer or the device of an
        order taken in against the wrong one. Only before the customer has
        the estimate: the delivery OTP verification, the M04 collector check
        and every estimate's customer approval were given by (and for) the
        old customer, so they are voided."""
        reason = self._fix_assert_supervisor_reason(
            "Correcting an order's customer or device", reason
        )
        customer = self.env["res.partner"].browse(self._fix_id(customer_id)).exists()
        device = self.env["fix.device"].browse(self._fix_id(device_id)).exists()
        if not customer and not device:
            raise UserError("Name the correct customer or device.")
        for order in self:
            if order.state not in _CORRECTABLE_STATES:
                raise UserError(
                    "Order %s is %s: the customer and device are corrected only before the "
                    "estimate goes to the customer. Cancel the order and raise a new one."
                    % (order.name, order.state)
                )
            if order.estimate_ids.filtered(lambda e: e.state != "draft"):
                raise UserError(
                    "Order %s has an estimate the customer has seen: cancel the order and raise "
                    "a new one for the right customer or device." % order.name
                )
            vals = {}
            notes = []
            if customer and customer != order.customer_id:
                vals["customer_id"] = customer.id
                notes.append(
                    "customer %s -> %s" % (order.customer_id.display_name, customer.display_name)
                )
            if device and device != order.device_id:
                vals["device_id"] = device.id
                notes.append(
                    "device %s -> %s" % (order.device_id.display_name, device.display_name)
                )
            if not vals:
                continue
            vals.update(order._fix_void_customer_evidence_vals())
            order._guarded().write(vals)
            order._fix_void_estimate_approvals()
            if "device_id" in vals:
                order._check_warranty_gate()
            order.message_post(
                body="Corrected by %s: %s. Reason: %s. The delivery OTP, the collector check "
                "and the estimates' customer approvals were voided."
                % (self.env.user.name, "; ".join(notes), reason)
            )
        return True

    def _fix_void_customer_evidence_vals(self) -> dict:
        vals = {
            "delivery_otp_verified": False,
            "delivery_otp_verified_at": False,
            "delivery_otp_verified_by": False,
            "delivery_otp_sent_at": False,
            "delivery_otp_expires_at": False,
            "delivery_otp_attempts": 0,
        }
        # the M04 collector check (cd_front_desk, read through the registry)
        for name in ("collector_id_verified_by", "collector_id_verified_at"):
            if name in self._fields:
                vals[name] = False
        return vals

    def _fix_void_estimate_approvals(self) -> None:
        self.ensure_one()
        self.sudo().write({"delivery_otp_digest": False})
        for est in self.sudo().estimate_ids:
            est.sudo().write({"customer_otp_digest": False})
            est._guarded().write(
                {
                    "customer_approval_ref": False,
                    "customer_approval_method": False,
                    "customer_approval_at": False,
                    "customer_approval_recorded_by": False,
                    "customer_approved_total": 0.0,
                    "customer_otp_expires_at": False,
                    "customer_otp_attempts": 0,
                }
            )

    # --------------------------------------------------- M01-07: LCI finding
    def action_correct_lci(self, tripped=None, reason=None, photo_attachment_id=None):
        """The liquid-contact finding decides whether the warranty covers the
        job (M01-F14). Recorded at intake; a Service Supervisor corrects it
        with a photo of the indicator uploaded on the order."""
        reason = self._fix_assert_supervisor_reason("Correcting the LCI finding", reason)
        value = str(tripped).strip().lower() in ("1", "true", "yes", "y", "tripped")
        named = self.env["ir.attachment"].browse(self._fix_id(photo_attachment_id)).exists()
        for order in self:
            if order.state in ("delivered", "closed", "cancelled"):
                raise UserError("Order %s is %s." % (order.name, order.state))
            # the photo named, else the newest image uploaded on the order
            photo = named or self.env["ir.attachment"].sudo().search(
                [
                    ("res_model", "=", order._name),
                    ("res_id", "=", order.id),
                    ("mimetype", "=like", "image/%"),
                ],
                order="id desc",
                limit=1,
            )
            att = photo.sudo()
            if att and not att.res_model:
                att.write({"res_model": order._name, "res_id": order.id})
            if not order._fix_own_attachment(photo, image=True):
                raise UserError(
                    "Upload the photo of the liquid-contact indicator on order %s first: the "
                    "correction is evidenced." % order.name
                )
            if order.lci_tripped == value:
                continue
            order._guarded().write({"lci_tripped": value})
            order.message_post(
                body="LCI finding corrected by %s to %s (photo %s). Reason: %s."
                % (self.env.user.name, "TRIPPED" if value else "not tripped", photo.name, reason)
            )
        return True

    # ------------------------------------------------ M01-15: branch transfer
    def action_transfer_branch(self, branch_id=None, reason=None):
        """Move a live order to another branch: the operating unit (record
        rules, GL dimensions, the SLA's branch users) follows the branch."""
        reason = self._fix_assert_supervisor_reason(
            "Transferring an order to another branch", reason
        )
        branch = self.env["fix.branch"].browse(self._fix_id(branch_id)).exists()
        if not branch:
            raise UserError("Name the branch the order moves to.")
        for order in self:
            if order.state in ("delivered", "closed", "cancelled"):
                raise UserError("Order %s is %s: it no longer moves." % (order.name, order.state))
            if branch == order.branch_id:
                continue
            company = branch.sudo().operating_unit_id.company_id
            if company and company != order.company_id:
                raise UserError(
                    "Branch %s belongs to %s, not to %s."
                    % (branch.name, company.name, order.company_id.name)
                )
            old = order.branch_id
            # posted before the move: the supervisor may not see the order
            # once it belongs to another branch's operating unit
            order.message_post(
                body="Transferred by %s from %s to %s. Reason: %s."
                % (self.env.user.name, old.display_name, branch.display_name, reason)
            )
            # the move itself is the system's (the record leaves the
            # supervisor's operating unit, so its tracking runs as sudo)
            order.sudo()._guarded().write(
                {
                    "branch_id": branch.id,
                    "operating_unit_id": branch.sudo().operating_unit_id.id or False,
                }
            )
        return True

    # ------------------------------------------------------ M01-05: close cron
    @api.model
    def _cron_close_delivered(self):
        """A02 pass 2 (M01-05): nothing closed a delivered order, so the OEM
        claim (raised before close), the post-closure survey and the close
        drain of the invoice waited on someone pressing Close. A delivered
        order whose close gate passes is closed (as a person would be:
        _fix_close_problem, never the superuser's bypass); the rest stay
        delivered and show on the M01 board as 'delivered, not closed'."""
        closed = 0
        for order in self.sudo().search([("state", "=", "delivered")], order="delivered_at, id"):
            try:
                with self.env.cr.savepoint():
                    order._fix_raise_warranty_claim()
                    if order._fix_close_problem():
                        continue
                    order._fix_advance("closed")
                    closed += 1
            except Exception:
                logger.exception("Close cron: order %s not closed", order.name)
        return closed

    # -------------------------------------------- M01-13: uncollected devices
    _UNCOLLECTED_BODY = {
        "en": "1000FiX: your repaired device (order {order}) has been ready for collection at "
        "{branch} for {days} days. Please collect it; call 16743.",
        "bn": "1000FiX: অর্ডার {order}-এর মেরামতকৃত ডিভাইসটি {days} দিন ধরে {branch}-এ সংগ্রহের "
        "অপেক্ষায়। অনুগ্রহ করে সংগ্রহ করুন; 16743।",
    }
    _UNCOLLECTED_NOTICE = {
        "en": "1000FiX FORMAL NOTICE: order {order} has been uncollected for {days} days. If it "
        "is not collected within {dispose} days of repair completion it is treated as abandoned "
        "and may be disposed of. Call 16743.",
        "bn": "1000FiX আনুষ্ঠানিক নোটিশ: অর্ডার {order} {days} দিন ধরে অসংগৃহীত। মেরামত শেষের "
        "{dispose} দিনের মধ্যে সংগ্রহ না করলে এটি পরিত্যক্ত গণ্য হবে। 16743।",
    }

    @api.model
    def _cron_uncollected_reminders(self):
        """D13: a Ready device is chased on the reminder days after Ready (3,
        7, 15, 30 by default); the last is the formal notice. Disposal (the
        abandoned flag, _cron_flag_abandoned) comes only at the disposal
        day. Each reminder goes once (uncollected_reminder_stage)."""
        policy = self._fix_uncollected_policy()
        now = fields.Datetime.now()
        sent = 0
        for order in self.sudo().search([("state", "=", "ready"), ("ready_at", "!=", False)]):
            days = (now - order.ready_at).days
            stage = max([d for d in policy["reminders"] if d <= days], default=0)
            if stage <= (order.uncollected_reminder_stage or 0):
                continue
            try:
                with self.env.cr.savepoint():
                    notice = stage >= policy["notice"]
                    order._fix_send_uncollected(stage, notice, policy)
                    vals = {"uncollected_reminder_stage": stage}
                    if notice and not order.uncollected_notice_at:
                        vals["uncollected_notice_at"] = now
                    order._guarded().write(vals)
                    sent += 1
            except Exception:
                logger.exception("Uncollected reminder for %s failed", order.name)
        return sent

    def _fix_send_uncollected(self, stage, notice, policy) -> None:
        """Queue the customer's SMS through the one notification exit (M27
        fix.notif.delivery, read through the registry: consent, curfew and
        evidence apply) and record it on the order; a formal notice also
        gives the branch supervisors a to-do."""
        self.ensure_one()
        values = {
            "order": self.name,
            "branch": self.branch_id.name or "the branch",
            "days": stage,
            "dispose": policy["dispose_after"],
        }
        bodies = self._UNCOLLECTED_NOTICE if notice else self._UNCOLLECTED_BODY
        Notif = self.env.get("fix.notif.delivery")
        queued = False
        if Notif is not None and self.customer_id:
            language = "en"
            if hasattr(Notif, "_preferred_language"):
                language = Notif._preferred_language(self.customer_id) or "en"
            try:
                with self.env.cr.savepoint():
                    Notif.sudo().queue(
                        channel="sms",
                        purpose="service_updates",
                        partner=self.customer_id,
                        body=(bodies.get(language) or bodies["en"]).format(**values),
                        lawful_basis="contract",
                        source_model=self._name,
                        source_id=self.id,
                        dedup_key="m01-uncollected:%s:%s" % (self.id, stage),
                        operating_unit=self.operating_unit_id or self.branch_id.operating_unit_id,
                        company=self.company_id,
                    )
                    queued = True
            except Exception as exc:  # no phone, no provider: the chatter says so
                logger.info("Uncollected SMS for %s not queued: %s", self.name, exc)
        self.message_post(
            body="%s: device uncollected %d days after Ready%s."
            % (
                "Formal uncollected-device notice" if notice else "Collection reminder",
                stage,
                "; SMS queued to the customer" if queued else "; no SMS could be queued",
            )
        )
        if notice:
            supervisors = self.env.ref(GROUP_SUPERVISOR, raise_if_not_found=False)
            for user in self._fix_branch_users(supervisors):
                self.activity_schedule(
                    "mail.mail_activity_data_todo",
                    summary="Uncollected device notice: %s" % self.name,
                    note="Formal notice issued %d days after Ready. Disposal is possible after "
                    "%d days, with a branch manager's approval." % (stage, policy["dispose_after"]),
                    user_id=user.id,
                )

    # --------------------------------------------- D4: on-site completion
    def action_complete_onsite(self, field_order):
        """D4 (stream S3 calls it from M02's field hand-back): an on-site
        order's field completion is its QC and its handover. The field
        order's customer sign-off and post-work photo (unless the field
        evidence profile is 'no_photo') stand as the evidence; the order
        moves to Delivered (the tax invoice is raised there, cd_billing_
        engine) and the field payment taken stays on it - a part payment
        leaves the rest due on the invoice (D3). Idempotent per field order."""
        self.ensure_one()
        allowed = self.env.su or any(
            self.env.ref(g, raise_if_not_found=False) and self.env.user.has_group(g)
            for g in _ONSITE_GROUPS
        )
        if not allowed:
            raise UserError("An on-site completion is recorded from the field order's hand-back.")
        Field = self.env.get("fix.field.order")
        field_order = (
            field_order.sudo()
            if hasattr(field_order, "_name")
            else (Field.sudo().browse(self._fix_id(field_order)) if Field is not None else None)
        )
        if not field_order or not field_order.exists():
            raise UserError("Name the completed field order.")
        if field_order.order_id != self:
            raise UserError(
                "Field order %s is not for order %s." % (field_order.display_name, self.name)
            )
        if self.state == "delivered" and self.onsite_field_order_ref == field_order.name:
            return True
        if self.service_type != "onsite":
            raise UserError(
                "Order %s is a %s order: only an on-site job is delivered in the field."
                % (self.name, self.service_type)
            )
        if field_order.state != "completed":
            raise UserError(
                "Field order %s is %s, not completed."
                % (field_order.display_name, field_order.state)
            )
        if self.state not in _ONSITE_FROM:
            raise UserError(
                "Order %s is %s: an on-site completion follows the approved repair."
                % (self.name, self.state)
            )
        self._check_commercial_clearance_onsite()
        profile = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(_FIELD_EVIDENCE_PROFILE_PARAM, "strict")
            or "strict"
        ).strip()
        missing = []
        if not field_order.customer_signature_attachment_id:
            missing.append("the customer's sign-off")
        if profile != "no_photo" and not field_order.post_work_photo_attachment_id:
            missing.append("the post-work photo")
        if missing:
            raise UserError(
                "Field order %s has no %s: an on-site job is delivered on the customer's "
                "sign-off and the post-work photo."
                % (field_order.display_name, " or ".join(missing))
            )
        extra = {
            "onsite_completed_at": fields.Datetime.now(),
            "onsite_field_order_ref": field_order.name,
            "recipient_name": field_order.customer_signature_signer or self.customer_id.name,
        }
        tech_user = field_order.technician_id.user_id
        if tech_user:
            extra["repair_completed_by"] = tech_user.id
        if self.payment_settlement_state == "unpaid" and self._fix_zero_charge_basis():
            extra["payment_settlement_state"] = "covered_zero_charge"
        self.with_context(**{_ONSITE_KEY: _ONSITE_TOKEN})._fix_advance("delivered", extra)
        photo = field_order.post_work_photo_attachment_id.sudo()
        if photo and not self.after_repair_photo_attachment_id:
            copy = photo.copy({"res_model": self._name, "res_id": self.id})
            self.sudo().write({"after_repair_photo_attachment_id": copy.id})
        self.message_post(
            body="Completed on site (field order %s): the customer's sign-off%s stand as QC and "
            "handover (D4)."
            % (field_order.display_name, " and the post-work photo" if photo else "")
        )
        return True

    def _check_commercial_clearance_onsite(self) -> None:
        """The work done on site was approved: an approved estimate or a
        zero-charge entitlement (the same test as the approval gate)."""
        if self._fix_zero_charge_basis():
            return
        if not self.estimate_ids.filtered(lambda e: e.state == "approved"):
            raise UserError(
                "Order %s has no approved estimate and no zero-charge entitlement: the on-site "
                "work cannot be delivered and invoiced." % self.name
            )

    # ------------------------------------------- X5-16: M15 part reservation
    def _fix_reserve_estimate_parts(self, estimate) -> None:
        """X5-16: the approved estimate's parts are held in M15 for this order
        (M15's own reservation, fix.stock.reservation, at the branch store),
        so another job cannot take them before the repair. A part M15 does
        not stock, or cannot hold, is reported on the order - the approval
        stands (BRU-SRM-15: a parts hold is the supervisor's)."""
        self.ensure_one()
        Reservation = self.env.get("fix.stock.reservation")
        if Reservation is None:
            return
        order = self.sudo()
        Part = self.env["fix.spare.part"].sudo()
        Location = self.env["fix.stock.location"].sudo()
        store = Location.search(
            [
                ("branch_id", "=", order.branch_id.id),
                ("location_type", "=", "branch"),
                ("state", "=", "active"),
                ("company_id", "=", order.company_id.id),
            ],
            limit=1,
        )
        held, not_held = [], []
        for line in estimate.sudo().line_ids.filtered(
            lambda ln: ln.line_type in STOCK_LINE_TYPES and ln.product_id and ln.quantity > 0
        ):
            part = Part.search(
                [
                    ("product_id", "=", line.product_id.id),
                    ("company_id", "in", [order.company_id.id, False]),
                ],
                limit=1,
            )
            if not part:
                continue  # not an M15 spare part (a service item)
            already = Reservation.sudo().search_count(
                [
                    ("service_order_ref", "=", order.name),
                    ("part_id", "=", part.id),
                    ("state", "=", "active"),
                ]
            )
            if already:
                continue
            if not store:
                not_held.append("%s (no branch store)" % part.part_number)
                continue
            try:
                with self.env.cr.savepoint():
                    res = Reservation.sudo().create(
                        {
                            "company_id": order.company_id.id,
                            "part_id": part.id,
                            "location_id": store.id,
                            "qty": line.quantity,
                            "service_order_ref": order.name,
                            "notes": "Estimate %s approved" % estimate.display_name,
                        }
                    )
                    res.action_reserve()
                    held.append("%s x %g (%s)" % (part.part_number, line.quantity, res.name))
            except Exception as exc:
                not_held.append("%s (%s)" % (part.part_number, exc))
        if held or not_held:
            order.message_post(
                body="Estimate approved: %s%s."
                % (
                    "parts held in M15: %s" % ", ".join(held) if held else "no part held",
                    "; NOT held: %s - reserve them in M15 or place a parts hold"
                    % "; ".join(not_held)
                    if not_held
                    else "",
                )
            )

    def _fix_release_part_reservations(self, label) -> None:
        """A cancelled order gives back the stock its estimate held."""
        self.ensure_one()
        Reservation = self.env.get("fix.stock.reservation")
        if Reservation is None:
            return
        for res in Reservation.sudo().search(
            [("service_order_ref", "=", self.sudo().name), ("state", "=", "active")]
        ):
            try:
                with self.env.cr.savepoint():
                    # M15's own release (as the system: the order is cancelled)
                    res._release_open("released", label)
            except Exception as exc:
                logger.info("Reservation %s of %s not released: %s", res.name, self.name, exc)

    def _fix_cancel_downstream(self, reason_code, note) -> None:
        super()._fix_cancel_downstream(reason_code, note)
        self._fix_release_part_reservations("Order %s cancelled (%s)" % (self.name, reason_code))
