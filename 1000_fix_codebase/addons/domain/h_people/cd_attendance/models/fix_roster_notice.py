# fix_roster_notice — M55 AUT-WFM-10 / FR-WFM-041/042: the rostered employee is told.
#
# A published roster and every approved change to a published slot are sent
# to the employee through the M27 delivery service (fix.notif.delivery.queue,
# cd_contact_centre): consent/lawful basis, BTRC window, provider and the
# delivery row are M27's. The basis is the employment contract (a roster is
# part of performing it), purpose "service_updates".
#
# Channel: the M27 queue API takes no stated channel preference (it reads only
# the preferred LANGUAGE), so the channel is SMS to the employee's mobile when
# one is recorded, else e-mail, as the M27 senders elsewhere do.
#
# Fallback: when M27 is not installed, or the employee has no contact partner
# or no phone/e-mail, the notice is a chatter message on each slot, the
# employee is made a follower, and a to-do activity is scheduled (for the
# employee's own login, else for the deciding supervisor, who must tell them).
#
# Idempotent: one fix.roster.notice per (event key, employee): a publication
# notifies each employee once, a change request once per affected employee,
# and a replay of either is a no-op (M27's own dedup_key carries the same key).
from odoo import api, fields, models
from odoo.exceptions import AccessError


def _hours(h):
    return "%02d:%02d" % (int(h), round((h - int(h)) * 60))


def _slot_line(slot):
    shift = slot.shift_id
    return "%s %s (%s-%s)" % (
        slot.date,
        shift.name or "",
        _hours(shift.start_hour),
        _hours(shift.end_hour),
    )


class FixRosterNotice(models.Model):
    """One roster notice to one employee (the idempotency record and the trail)."""

    _name = "fix.roster.notice"
    _description = "Roster Notice to an Employee"
    _order = "id desc"

    key = fields.Char(required=True, index=True, readonly=True)
    employee_id = fields.Many2one("hr.employee", required=True, index=True, readonly=True)
    company_id = fields.Many2one("res.company", required=True, index=True, readonly=True)
    kind = fields.Selection(
        [("published", "Roster Published"), ("changed", "Slot Changed")],
        required=True,
        readonly=True,
    )
    slot_ids = fields.Many2many("fix.roster.slot", string="Slots", readonly=True)
    route = fields.Selection(
        [("m27", "M27 Delivery"), ("chatter", "Chatter + Activity (fallback)")],
        required=True,
        readonly=True,
    )
    channel = fields.Char(readonly=True)
    delivery_id = fields.Integer(string="M27 Delivery", readonly=True)
    delivery_state = fields.Char(readonly=True)
    fallback_reason = fields.Char(readonly=True)
    body = fields.Text(readonly=True)

    _key_employee = models.Constraint(
        "UNIQUE (key, employee_id)", "An employee is told of one roster event once"
    )

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            raise AccessError("Roster notices are written by the roster workflow only.")
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.su:
            raise AccessError("Roster notices are written by the roster workflow only.")
        return super().write(vals)

    # ---- addressing ------------------------------------------------------------
    @api.model
    def _fix_contact(self, employee):
        """(partner, channel, address, why-not)."""
        emp = employee.sudo()
        partner = (emp.work_contact_id if "work_contact_id" in emp._fields else False) or (
            emp.user_id.partner_id
        )
        phone = (emp.mobile_phone or "").strip()
        if not phone and partner:
            phone = (getattr(partner, "mobile", False) or partner.phone or "").strip()
        email = (emp.work_email or "").strip() or ((partner.email or "").strip() if partner else "")
        if not partner:
            return partner, None, None, "the employee has no contact partner"
        if phone:
            return partner, "sms", phone, ""
        if email:
            return partner, "email", email, ""
        return partner, None, None, "no mobile number or e-mail is recorded for the employee"

    # ---- sending -----------------------------------------------------------------
    @api.model
    def _fix_send(self, key, kind, employee, slots, subject, body, fallback_user=None, thread=None):
        """Tell `employee` once about `slots`; returns the fix.roster.notice.
        `thread` carries the chatter trail when no slot is left (a removal)."""
        Notice = self.sudo()
        done = Notice.search([("key", "=", key), ("employee_id", "=", employee.id)], limit=1)
        if done:
            return done
        slots = slots.sudo()
        targets = slots or (thread.sudo() if thread else slots)
        company = slots[:1].company_id or employee.sudo().company_id or self.env.company
        partner, channel, address, why = self._fix_contact(employee)
        Delivery = self.env.get("fix.notif.delivery")
        vals = {
            "key": key,
            "employee_id": employee.id,
            "company_id": company.id,
            "kind": kind,
            "slot_ids": [(6, 0, slots.ids)],
            "body": body,
        }
        if Delivery is not None and channel:
            delivery = Delivery.sudo().queue(
                channel=channel,
                purpose="service_updates",
                partner=partner,
                to_address=address,
                subject=subject,
                body=body,
                lawful_basis="contract",
                source_model="fix.roster.slot",
                source_id=slots[:1].id,
                dedup_key="m55-roster:%s:%d" % (key, employee.id),
                company=company,
            )
            vals.update(
                route="m27",
                channel=channel,
                delivery_id=delivery.id,
                delivery_state=delivery.state,
            )
            for target in targets:
                target.message_post(
                    body="%s Sent to %s by M27 %s (delivery %d, %s)."
                    % (subject, employee.sudo().name, channel, delivery.id, delivery.state)
                )
            return Notice.create(vals)
        vals.update(
            route="chatter",
            fallback_reason=("M27 delivery is not installed" if Delivery is None else why)[:250],
        )
        user = employee.sudo().user_id or fallback_user or self.env.user
        todo = self.env.ref("mail.mail_activity_data_todo", raise_if_not_found=False)
        for target in targets:
            if partner:
                target.message_subscribe(partner_ids=partner.ids)
            target.message_post(
                body="%s %s (Not sent by M27: %s.)" % (subject, body, vals["fallback_reason"]),
                partner_ids=partner.ids if partner else [],
                subtype_xmlid="mail.mt_comment",
            )
            if todo and hasattr(target, "activity_schedule"):
                target.activity_schedule(
                    activity_type_id=todo.id,
                    summary=subject[:80],
                    note=body,
                    user_id=user.id,
                )
        return Notice.create(vals)


class FixRosterPublicationNotice(models.Model):
    _inherit = "fix.roster.publication"

    def _fix_notify_published(self):
        """Each rostered employee is told their published slots, once."""
        Notice = self.env["fix.roster.notice"]
        for pub in self.sudo().filtered(lambda p: p.state == "published"):
            for employee in pub.slot_ids.mapped("employee_id"):
                mine = pub.slot_ids.filtered(lambda s, e=employee: s.employee_id == e).sorted(
                    "date"
                )
                Notice._fix_send(
                    "publication:%d" % pub.id,
                    "published",
                    employee,
                    mine,
                    "1000FiX রোস্টার / Roster published:",
                    "your shifts: %s." % "; ".join(_slot_line(s) for s in mine),
                    fallback_user=pub.decided_by_id,
                )
        return True

    def action_approve(self):
        res = super().action_approve()
        self._fix_notify_published()
        return res


class FixRosterChangeNotice(models.Model):
    _inherit = "fix.roster.change.request"

    def _fix_notify_changed(self):
        """The employee(s) of an applied change are told, once per change."""
        Notice = self.env["fix.roster.notice"]
        for req in self.sudo().filtered(lambda r: r.state == "approved"):
            slot = req.slot_id
            was = "%s %s" % (req.old_date, req.old_shift_id.name or "")
            if req.kind == "remove" or not slot:
                text = "your shift of %s is removed (%s)." % (was, req.reason)
            else:
                text = "your shift of %s is now %s (%s)." % (was, _slot_line(slot), req.reason)
            for employee in req.old_employee_id | (
                slot.employee_id if slot else req.old_employee_id
            ):
                Notice._fix_send(
                    "change:%d" % req.id,
                    "changed",
                    employee,
                    slot if slot else self.env["fix.roster.slot"],
                    "1000FiX রোস্টার / Roster changed:",
                    text,
                    fallback_user=req.decided_by_id,
                    thread=req,
                )
        return True

    def action_approve(self):
        res = super().action_approve()
        self._fix_notify_changed()
        return res
