# fix_field_order_redispatch — A07 P1 wiring round 2 (2026-11-04): M46 tells
# M02 a van is off the road, and when it is back.
#
# AUT-FLT-02 / FF-48: M46 published vehicle.off_road and vehicle.available
# and nobody listened, so a van taken off the road for failed brakes stayed
# on every field order booked in it: the dispatcher found out when the
# technician rang from the yard. The vehicle link of a field order lives in
# this bridge, so the consumer lives here too:
#   vehicle.off_road  -> every open field order in that van for today or a
#                        later day is FLAGGED for re-dispatch (a field and a
#                        dispatcher activity; its state is never touched), and
#                        the van's assignments from today mark the conflict;
#   vehicle.available -> the flags that off-road record set are cleared, with
#                        who returned the van and when (repointed instead
#                        while another off-road record still holds the van).
# The dispatcher resolves a flag by re-dispatching the order with another van
# (recorded as theirs) or by waiting for the van. Nobody types a flag: the
# fields are guarded, and only the consumers and the re-dispatch write them.
from odoo import api, fields, models
from odoo.addons.cd_field_service.models.fix_field_order import DISPATCHER_GROUP
from odoo.addons.cd_vehicle_ext.models.fix_vehicle_ops import dhaka_today

_CLOSED = ("completed", "cancelled")
REDISPATCH_FIELDS = frozenset(
    {
        "redispatch_required",
        "redispatch_offroad_id",
        "redispatch_reason",
        "redispatch_flagged_at",
        "redispatch_cleared_at",
        "redispatch_cleared_by_id",
        "redispatch_clear_note",
        "redispatch_activity_id",
    }
)
CONFLICT_FIELDS = frozenset(
    {
        "offroad_conflict_id",
        "offroad_conflict_note",
        "offroad_conflict_cleared_at",
        "offroad_conflict_cleared_by_id",
    }
)


def _label(vehicle):
    vehicle = vehicle.sudo()
    return vehicle.name or vehicle.license_plate or ""


def _offroad_text(off):
    off = off.sudo()
    causes = dict(off._fields["cause"].selection)
    return "off the road since %s (%s, %s: %s)" % (
        off.started_on,
        off.name,
        causes.get(off.cause, off.cause or "-"),
        off.reason or "-",
    )


class FixVehicleAssignmentOffroadConflict(models.Model):
    # The conflict fields are unforgeable (the model carries the guard mixin):
    # only the off-road consumers and the move below write them.
    _inherit = "fix.vehicle.assignment"

    offroad_conflict_id = fields.Many2one(
        "fix.vehicle.offroad",
        string="Off-Road Conflict",
        readonly=True,
        copy=False,
        index=True,
        ondelete="set null",
        help="The van was taken off the road while booked for this day (M46).",
    )
    offroad_conflict_note = fields.Text(string="Conflict", readonly=True, copy=False)
    offroad_conflict_cleared_at = fields.Datetime(
        string="Conflict Cleared At", readonly=True, copy=False
    )
    offroad_conflict_cleared_by_id = fields.Many2one(
        "res.users", string="Conflict Cleared By", readonly=True, copy=False
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | CONFLICT_FIELDS

    def write(self, vals):
        res = super().write(vals)
        if "vehicle_id" in vals:
            # the booking moved to another van (re-dispatch): the off-road
            # conflict of the old van no longer applies to it
            for rec in self.sudo().filtered(
                lambda a: a.offroad_conflict_id and a.offroad_conflict_id.vehicle_id != a.vehicle_id
            ):
                note = "Moved by %s to vehicle %s: the conflict with %s no longer applies." % (
                    self.env.user.name,
                    _label(rec.vehicle_id),
                    rec.offroad_conflict_id.name,
                )
                rec._guarded().write(
                    {
                        "offroad_conflict_id": False,
                        "offroad_conflict_cleared_at": fields.Datetime.now(),
                        "offroad_conflict_cleared_by_id": self.env.uid,
                        "offroad_conflict_note": note,
                    }
                )
                rec.message_post(body=note)
        return res


class FixFieldOrderRedispatch(models.Model):
    _inherit = "fix.field.order"

    redispatch_required = fields.Boolean(
        string="Re-Dispatch Required",
        readonly=True,
        copy=False,
        index=True,
        tracking=True,
        help="The vehicle this order travels in was taken off the road (M46): "
        "re-dispatch it with another vehicle, or wait for the van to return.",
    )
    redispatch_offroad_id = fields.Many2one(
        "fix.vehicle.offroad",
        string="Vehicle Off-Road",
        readonly=True,
        copy=False,
        index=True,
        ondelete="set null",
    )
    redispatch_reason = fields.Text(string="Re-Dispatch Reason", readonly=True, copy=False)
    redispatch_flagged_at = fields.Datetime(string="Flagged At", readonly=True, copy=False)
    redispatch_cleared_at = fields.Datetime(string="Flag Cleared At", readonly=True, copy=False)
    redispatch_cleared_by_id = fields.Many2one(
        "res.users", string="Flag Cleared By", readonly=True, copy=False
    )
    redispatch_clear_note = fields.Text(string="How It Was Cleared", readonly=True, copy=False)
    redispatch_activity_id = fields.Many2one(
        "mail.activity",
        string="Dispatcher Activity",
        readonly=True,
        copy=False,
        ondelete="set null",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | REDISPATCH_FIELDS

    def write(self, vals):
        res = super().write(vals)
        if "vehicle_id" in vals:
            # the dispatcher re-dispatched a flagged order with another van
            # (or none): the flag is resolved, and the resolution is theirs
            moved = self.sudo().filtered(
                lambda r: r.redispatch_required
                and r.vehicle_id != r.redispatch_offroad_id.vehicle_id
            )
            for rec in moved:
                rec._redispatch_clear(
                    "Re-dispatched by %s with %s."
                    % (
                        self.env.user.name,
                        "vehicle %s" % _label(rec.vehicle_id) if rec.vehicle_id else "no vehicle",
                    ),
                    self.env.user,
                )
        return res

    # ------------------------------------------------------------ helpers
    @api.model
    def _redispatch_orders(self, vehicle):
        """The open orders in `vehicle` for today (Dhaka) or a later day."""
        today = dhaka_today(self)
        orders = self.sudo().search(
            [("vehicle_id", "=", vehicle.id), ("state", "not in", _CLOSED)],
            order="scheduled_start asc, id asc",
        )
        return orders.filtered(lambda o: o._fix_vehicle_day() >= today)

    def _redispatch_dispatcher(self):
        """The dispatcher told: one active internal member of the dispatcher
        group in the order's company. Never the superuser."""
        self.ensure_one()
        group = self.env.ref(DISPATCHER_GROUP, raise_if_not_found=False)
        if not group:
            return self.env["res.users"]
        users = group.sudo().all_user_ids.filtered(
            lambda u: u.active
            and u._is_internal()
            and not u._is_superuser()
            and self.company_id in u.company_ids
        )
        return users.sorted("id")[:1]

    def _redispatch_clear(self, note, user):
        """Clear this order's flag: who and when are recorded, the dispatcher's
        activity is marked done with the reason. The order keeps whatever the
        dispatcher did with it."""
        for rec in self.sudo():
            rec._guarded().write(
                {
                    "redispatch_required": False,
                    "redispatch_cleared_at": fields.Datetime.now(),
                    "redispatch_cleared_by_id": user.id if user else False,
                    "redispatch_clear_note": note,
                }
            )
            activity = rec.redispatch_activity_id.exists()
            if activity:
                activity.action_feedback(feedback=note)
            rec.message_post(body="Re-dispatch flag cleared: %s" % note)

    # ------------------------------------------------------------ consumers
    @api.model
    def consume_vehicle_off_road(self, event):
        """vehicle.off_road -> each open field order in that van for today or
        later is flagged for re-dispatch once (a field, a dispatcher activity,
        a chatter note; never a state change), and each of the van's
        assignments from today marks the conflict. Idempotent: an order (or
        an assignment) already flagged is left as it is."""
        Off = self.env["fix.vehicle.offroad"].sudo()
        off = Off.browse(event.get("aggregate_id")).exists()
        if not off or off.state != "offroad":
            return False
        vehicle = off.vehicle_id
        today = dhaka_today(self)
        what = "Vehicle %s is %s." % (_label(vehicle), _offroad_text(off))
        for order in self._redispatch_orders(vehicle):
            if order.redispatch_required:
                continue  # flagged already (by this or another open off-road record)
            text = (
                "%s Field order %s (%s, %s) travels in it: re-dispatch it with another "
                "vehicle, or reschedule it after the van returns to service. The order "
                "itself is unchanged."
                % (
                    what,
                    order.name,
                    dict(order._fields["state"].selection).get(order.state),
                    order._fix_vehicle_day(),
                )
            )
            user = order._redispatch_dispatcher()
            activity = self.env["mail.activity"]
            if user:
                activity = order.activity_schedule(
                    "mail.mail_activity_data_todo",
                    date_deadline=today,
                    summary="Re-dispatch: vehicle %s off the road" % _label(vehicle),
                    note=text,
                    user_id=user.id,
                )
            order._guarded().write(
                {
                    "redispatch_required": True,
                    "redispatch_offroad_id": off.id,
                    "redispatch_reason": text,
                    "redispatch_flagged_at": fields.Datetime.now(),
                    "redispatch_cleared_at": False,
                    "redispatch_cleared_by_id": False,
                    "redispatch_clear_note": False,
                    "redispatch_activity_id": activity.id or False,
                }
            )
            order.message_post(body=text)
        Assignment = self.env["fix.vehicle.assignment"].sudo()
        for assignment in Assignment.search(
            [("vehicle_id", "=", vehicle.id), ("date", ">=", today)]
        ):
            if assignment.offroad_conflict_id:
                continue
            note = "%s It is booked for %s: rebook the crew in another vehicle." % (
                what,
                assignment.date,
            )
            assignment._guarded().write(
                {
                    "offroad_conflict_id": off.id,
                    "offroad_conflict_note": note,
                    "offroad_conflict_cleared_at": False,
                    "offroad_conflict_cleared_by_id": False,
                }
            )
            assignment.message_post(body=note)
        return True

    @api.model
    def consume_vehicle_available(self, event):
        """vehicle.available -> the flags this off-road record set are cleared
        (who returned the van, and when). While another off-road record still
        holds the van, the flag is moved onto it instead. Idempotent: only
        flags that still name this record are touched."""
        Off = self.env["fix.vehicle.offroad"].sudo()
        off = Off.browse(event.get("aggregate_id")).exists()
        if not off or off.state != "returned":
            return False
        vehicle = off.vehicle_id
        still = Off.search(
            [("vehicle_id", "=", vehicle.id), ("state", "=", "offroad"), ("id", "!=", off.id)],
            order="id asc",
            limit=1,
        )
        who = off.returned_by_id
        payload = event.get("payload") or {}
        back = "Vehicle %s returned to service on %s (%s) by %s" % (
            _label(vehicle),
            payload.get("effective_from") or off.ended_on or "-",
            off.name,
            who.name or "the system",
        )
        orders = self.sudo().search(
            [("redispatch_offroad_id", "=", off.id), ("redispatch_required", "=", True)]
        )
        assignments = (
            self.env["fix.vehicle.assignment"].sudo().search([("offroad_conflict_id", "=", off.id)])
        )
        if still:
            text = "%s, but it is still %s." % (back, _offroad_text(still))
            for order in orders:
                order._guarded().write(
                    {"redispatch_offroad_id": still.id, "redispatch_reason": text}
                )
                order.message_post(body=text)
            for assignment in assignments:
                assignment._guarded().write(
                    {"offroad_conflict_id": still.id, "offroad_conflict_note": text}
                )
                assignment.message_post(body=text)
            return True
        orders._redispatch_clear("%s." % back, who)
        for assignment in assignments:
            assignment._guarded().write(
                {
                    "offroad_conflict_id": False,
                    "offroad_conflict_cleared_at": fields.Datetime.now(),
                    "offroad_conflict_cleared_by_id": who.id or False,
                    "offroad_conflict_note": "%s: the booking stands again." % back,
                }
            )
            assignment.message_post(body="%s: the booking stands again." % back)
        return True
