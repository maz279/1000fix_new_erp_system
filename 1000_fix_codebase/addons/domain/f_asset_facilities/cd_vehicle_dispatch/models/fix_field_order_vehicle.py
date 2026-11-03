# fix_field_order_vehicle — M46 -> M02 bridge: the vehicle a field order
# travels in, gated at dispatch.
#
# A07 audit (2026-11-03) M46-1: the dispatch gate was not connected to
# dispatch. fix.field.order had no vehicle, action_dispatch never consulted
# M46, and nothing created a fix.vehicle.assignment, so an uninsured or unfit
# van went out unchecked (BRU-FLT-02, AC-02 "UI, API or dispatch engine").
# A bridge module, not cd_field_service or cd_vehicle_ext: M02 does not need
# to know M46 exists, cd_vehicle_ext stays independent of M02, and a database
# that has not installed this bridge never loads the fix.field.order extension.
from odoo import api, fields, models
from odoo.addons.cd_vehicle_ext.models.fix_vehicle import param_on
from odoo.addons.cd_vehicle_ext.models.fix_vehicle_ops import DHAKA_TZ, dhaka_today
from odoo.exceptions import UserError, ValidationError

# Whether dispatch REQUIRES a vehicle. Off by default: no live field order has
# one, and walk-in or motorbike jobs may not use a fleet van. With it off, a
# field order that names a vehicle is still gated. A business decision.
REQUIRE_VEHICLE_PARAM = "cd_vehicle_dispatch.dispatch_requires_vehicle"

# The states in which the order is on the road with its van.
_LIVE_STATES = ("dispatched", "accepted", "en_route", "arrived", "in_progress")
# The states in which the order no longer holds the van for the day.
_RELEASED_STATES = ("draft", "pending_dispatch", "declined", "cancelled")
_VEHICLE_FIELDS = frozenset({"vehicle_id", "vehicle_driver_id"})
# Changing these on a live order refreshes (and re-gates) its assignment.
_SYNC_FIELDS = _VEHICLE_FIELDS | {"technician_id", "scheduled_start"}

# In-process token: action_dispatch syncs once after its own writes. An
# object, not a flag, so an RPC caller cannot put it in the context to skip
# the sync on a write of vehicle_id.
_DEFER_KEY = "fix_vehicle_sync_deferred"
_DEFER = object()


class FixVehicleAssignmentDispatch(models.Model):
    _inherit = "fix.vehicle.assignment"

    # The M02 field orders this van serves that day (one assignment per van
    # per day; several orders share it when the crew is the same).
    field_order_ids = fields.One2many(
        "fix.field.order", "vehicle_assignment_id", string="Field Orders"
    )
    dispatch_created = fields.Boolean(
        string="Made by Dispatch",
        readonly=True,
        copy=False,
        help="Created by M02 dispatch; removed when no field order holds it any more.",
    )


class FixFieldOrderVehicle(models.Model):
    _inherit = "fix.field.order"

    vehicle_id = fields.Many2one(
        "fleet.vehicle", string="Vehicle", index=True, tracking=True, ondelete="restrict"
    )
    vehicle_driver_id = fields.Many2one(
        "fix.driver",
        string="Vehicle Driver",
        tracking=True,
        ondelete="restrict",
        help="Who drives the vehicle; empty = the vehicle's assigned driver.",
    )
    vehicle_assignment_id = fields.Many2one(
        "fix.vehicle.assignment",
        string="Vehicle Assignment",
        readonly=True,
        copy=False,
        index=True,
        ondelete="set null",
    )

    def _fix_guarded_fields(self) -> set:
        # Only the dispatch sync links an order to an assignment.
        return super()._fix_guarded_fields() | {"vehicle_assignment_id"}

    # ---------------------------------------------------------------- dispatch
    def action_dispatch(self, technician_id=None):
        self._fix_require_dispatcher("Dispatching a field order")
        if param_on(self.env, REQUIRE_VEHICLE_PARAM):
            missing = self.filtered(lambda r: not r.vehicle_id)
            if missing:
                raise UserError(
                    "Name the vehicle before dispatching %s." % ", ".join(missing.mapped("name"))
                )
        res = super(
            FixFieldOrderVehicle, self.with_context(**{_DEFER_KEY: _DEFER})
        ).action_dispatch(technician_id=technician_id)
        # The gate runs here, inside the dispatch transaction: a refusal rolls
        # the whole dispatch back, so no order is dispatched in a refused van.
        self._fix_sync_vehicle_assignment()
        return res

    def write(self, vals):
        touched = _VEHICLE_FIELDS & set(vals)
        if touched and not self._fix_guard_open():
            closed = self.filtered(
                lambda r: r.state in ("completed", "cancelled")
                and any(r._fix_guard_differs(n, vals[n], r[n]) for n in touched)
            )
            if closed:
                raise UserError(
                    "Cannot change the vehicle on a completed or cancelled field order: "
                    "it keeps what it was closed with."
                )
        res = super().write(vals)
        if self.env.context.get(_DEFER_KEY) is not _DEFER:
            if _SYNC_FIELDS & set(vals):
                # M46-4 for M02: a van, driver, technician or day changed after
                # dispatch is gated again (reassignment included).
                self.filtered(
                    lambda r: r.state in _LIVE_STATES or r.state in _RELEASED_STATES
                )._fix_sync_vehicle_assignment()
            elif "state" in vals:
                # declined / cancelled / sent back: the van is free again. The
                # job's own progress (accept, arrive, start) is not re-gated:
                # the van was checked when it was dispatched.
                self.filtered(lambda r: r.state in _RELEASED_STATES)._fix_sync_vehicle_assignment()
        return res

    # ------------------------------------------------------- the assignment
    def _fix_vehicle_day(self):
        """The Dhaka date the van is needed: the scheduled start, else today."""
        self.ensure_one()
        if self.scheduled_start:
            return fields.Datetime.context_timestamp(
                self.with_context(tz=DHAKA_TZ), self.scheduled_start
            ).date()
        return dhaka_today(self)

    def _fix_sync_vehicle_assignment(self):
        """Create or refresh the day's fix.vehicle.assignment for each order.

        One van, one assignment per day (the overlap rule): several orders on
        the same day share it when the crew is the same; a different
        technician or driver on that van that day is refused. The assignment
        write runs the M46 gate. Written as superuser so an operating-unit
        rule on assignments cannot hide a conflict; the gate itself does not
        trust superuser. Reads are superuser too: the dispatcher need not hold
        the fleet officer's read rights on the van and driver."""
        Assignment = self.env["fix.vehicle.assignment"].sudo()
        for rec in self:
            srec = rec.sudo()
            previous = srec.vehicle_assignment_id
            if srec.state in _RELEASED_STATES or not srec.vehicle_id:
                if previous:
                    rec._guarded().write({"vehicle_assignment_id": False})
                    rec._fix_drop_orphan(previous)
                continue
            if srec.state not in _LIVE_STATES:
                continue
            day = srec._fix_vehicle_day()
            driver = srec.vehicle_driver_id or srec.vehicle_id.fix_driver_id
            tech = srec.technician_id
            target = Assignment.search(
                [("vehicle_id", "=", srec.vehicle_id.id), ("date", "=", day)], limit=1
            )
            crew = {
                "driver_id": driver.id or False,
                "technician_id": tech.id or False,
                "order_id": srec.order_id.id or False,
            }
            if target:
                others = target.field_order_ids - srec
                clash = (target.technician_id and tech and target.technician_id != tech) or (
                    target.driver_id and driver and target.driver_id != driver
                )
                if clash and (others or target != previous):
                    raise ValidationError(
                        "Vehicle %s is already assigned on %s to %s: a van cannot be in "
                        "two places."
                        % (
                            srec.vehicle_id.name or srec.vehicle_id.license_plate,
                            day,
                            ", ".join(
                                n for n in (target.technician_id.name, target.driver_id.name) if n
                            )
                            or "another crew",
                        )
                    )
                if others:
                    # shared van: keep the day's crew, fill only what is empty
                    target.write({k: v for k, v in crew.items() if v and not target[k]})
                else:
                    target.write(crew)
                target._fix_check_dispatchable()
            elif previous and not (previous.field_order_ids - srec):
                # this order's own assignment moves with it (write re-gates)
                previous.write({"vehicle_id": srec.vehicle_id.id, "date": day, **crew})
                target = previous
            else:
                target = Assignment.create(
                    {
                        "vehicle_id": srec.vehicle_id.id,
                        "date": day,
                        "company_id": srec.company_id.id,
                        "operating_unit_id": srec.operating_unit_id.id or False,
                        "dispatch_created": True,
                        **crew,
                    }
                )
            if previous != target:
                rec._guarded().write({"vehicle_assignment_id": target.id})
                if previous:
                    rec._fix_drop_orphan(previous)

    @api.model
    def _fix_drop_orphan(self, assignment):
        """An assignment dispatch made, that no order holds any more, frees the
        van for the day. One recorded by hand is left alone."""
        assignment = assignment.sudo().exists()
        if assignment and assignment.dispatch_created and not assignment.field_order_ids:
            assignment.unlink()
