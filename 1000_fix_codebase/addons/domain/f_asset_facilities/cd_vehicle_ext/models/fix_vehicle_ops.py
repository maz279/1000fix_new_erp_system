# fix_vehicle_ops — M46: drivers, statutory documents, off-road records, daily
# pre-use checks, PM by odometer, fuel transactions, telematics snapshots and
# accidents. The vehicle register (fleet.vehicle extension) and dispatch
# assignments live in fix_vehicle.py.
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

# A07 audit (2026-11-03) M46-2/M46-5: statutory dates are Bangladesh dates. A
# server-side "today" in UTC flips at 06:00 Dhaka, so a certificate ending
# today read as expired before the working day began.
DHAKA_TZ = "Asia/Dhaka"

# A07 P0 recipe (2026-11-03) M46-9, FR-FLT-034 "quantity exceeding tank
# capacity": no vehicle records its tank size, so one fleet-wide ceiling in
# litres. 100 L is above the tank of any van or motorbike the fleet runs, so
# it flags only the implausible fill; the business must confirm it (or set
# it per class once a class profile exists).
TANK_CAPACITY_PARAM = "cd_vehicle_ext.fuel_tank_capacity_litres"
TANK_CAPACITY_DEFAULT = 100.0

# FR-FLT-034 / BRU-FLT-09/10: the exception rules a fill is checked against.
# A flagged fill is HELD for review by someone other than its recorder.
FUEL_EXCEPTIONS = {
    "odometer_back": "odometer below the previous fill",
    "over_capacity": "litres above the tank capacity",
    "duplicate": "duplicate fill (same vehicle, date and litres)",
    "offroad": "vehicle was off-road on the fill date",
}

# Accident claim settlement (M46-10). The spec names the CFO for insurance
# (§13 R03) but gives no amounts, so this reuses the estate's asset/cost
# ladder, cd_rental_asset/models/fix_rental_fleet.py:28 (A05 fleet asset
# write-off): nothing at stake is tier 0, then Tier 2 up to BDT 250k, Tier 3
# up to 1M, Tier 4 above. A DEFAULT THE BUSINESS MUST CONFIRM (decision B2);
# an approval-matrix row can re-route it per model without code.
ACCIDENT_SETTLEMENT_DOFA_THRESHOLDS = [
    (0.0, "tier_0"),
    (250000.0, "tier_2"),
    (1000000.0, "tier_3"),
    (float("inf"), "tier_4"),
]


def dhaka_today(record):
    """Today's date in Dhaka, whatever the caller's own timezone setting."""
    return fields.Date.context_today(record.with_context(tz=DHAKA_TZ))


def _reason(text, what):
    """A stated reason, or a refusal naming what needs one."""
    text = (text or "").strip() if isinstance(text, str) else text
    if not text:
        raise UserError("Give the reason for %s." % what)
    return str(text)


class FixVehicleLockMixin(models.AbstractModel):
    """fix.guarded.mixin plus the fields a record freezes once it reaches a
    state (A07 P0 recipe: terminal states are immutable for users).

    The guard covers what only a transition may set; this covers what a user
    could set before (a damage cost, a PM's odometer) but must not change
    after (the claim is closed, the PM is done). Like the guard, writing the
    value a field already has passes, because the P03 form posts every field
    it shows; superuser code and transitions stay trusted."""

    _name = "fix.vehicle.lock.mixin"
    _inherit = ["fix.guarded.mixin"]
    _description = "M46 Workflow Guard and State Lock"

    def _fix_frozen_fields(self) -> set:
        """Fields THIS record no longer lets a user change. Override."""
        return set()

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        for rec in self[:1]:
            locked |= rec._fix_frozen_fields()
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                frozen = rec._fix_frozen_fields() & set(vals)
                changed = [n for n in frozen if rec._fix_guard_differs(n, vals[n], rec[n])]
                if changed:
                    labels = ", ".join(sorted(rec._fields[n].string or n for n in changed))
                    raise UserError(
                        "%s can no longer be changed on %s %s."
                        % (labels, rec._description, rec.display_name)
                    )
        return super().write(vals)


class FixDriver(models.Model):
    _name = "fix.driver"
    _description = "Fleet Driver"
    # A07 P0 recipe M46-6 / M46-20: suspension and reinstatement left no
    # trail; the chatter records who did it and why.
    _inherit = ["mail.thread", "fix.vehicle.lock.mixin"]
    _order = "name"

    name = fields.Char(required=True)
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, ondelete="restrict", index=True
    )
    license_no = fields.Char(string="Driving Licence No", required=True)
    license_class = fields.Char(string="Licence Class")
    license_expiry = fields.Date(string="Licence Expiry")
    phone = fields.Char()
    state = fields.Selection(
        [("active", "Active"), ("suspended", "Suspended")],
        required=True,
        default="active",
        tracking=True,
    )
    suspended_by_id = fields.Many2one(
        "res.users",
        string="Suspended By",
        readonly=True,
        copy=False,
        help="Who suspended the driver. They cannot reinstate the same driver.",
    )

    _employee_unique = models.Constraint("UNIQUE (employee_id)", "One driver record per employee")

    def _fix_guarded_fields(self) -> set:
        # A07 P0 recipe M46-6 (D1): any employee reinstated a suspended
        # driver by writing state='active'. The state moves only through
        # action_suspend / action_reinstate, which take a reason.
        return super()._fix_guarded_fields() | {"state", "suspended_by_id"}

    def action_suspend(self, reason=None):
        reason = _reason(reason, "suspending the driver")
        for rec in self:
            if rec.state != "active":
                raise UserError("Suspend an active driver")
            rec._guarded().write({"state": "suspended", "suspended_by_id": self.env.uid})
            rec.message_post(
                body="Driver suspended by %s. Reason: %s" % (self.env.user.name, reason)
            )
        return True

    def action_reinstate(self, reason=None):
        """Reinstatement: a second person, a reason, and a licence in date.

        The suspender cannot lift their own suspension (§13 SoD pattern),
        and reinstating a driver whose licence has lapsed or is unrecorded
        would put an unlicensed driver back on the eligible list (BRU-FLT-05)."""
        reason = _reason(reason, "reinstating the driver")
        today = dhaka_today(self)
        for rec in self:
            if rec.state != "suspended":
                raise UserError("Reinstate a suspended driver")
            if not self.env.su and rec.suspended_by_id == self.env.user:
                raise UserError(
                    "Segregation of duties: you suspended %s; another person must "
                    "reinstate them." % rec.name
                )
            if not rec.license_expiry or rec.license_expiry < today:
                raise UserError(
                    "%s cannot be reinstated: the driving licence %s. Record the "
                    "renewed licence first."
                    % (
                        rec.name,
                        "expired on %s" % rec.license_expiry
                        if rec.license_expiry
                        else "has no expiry date recorded",
                    )
                )
            rec._guarded().write({"state": "active", "suspended_by_id": False})
            rec.message_post(
                body="Driver reinstated by %s. Reason: %s" % (self.env.user.name, reason)
            )
        return True


class FixVehicleDocument(models.Model):
    _name = "fix.vehicle.document"
    _description = "Vehicle Statutory Document"
    _inherit = ["fix.guarded.mixin"]
    _order = "valid_to desc, id desc"

    name = fields.Char(required=True, default="New")
    vehicle_id = fields.Many2one(
        "fleet.vehicle", string="Vehicle", required=True, ondelete="cascade", index=True
    )
    doc_type = fields.Selection(
        [
            ("fitness", "Fitness Certificate"),
            ("insurance", "Insurance"),
            ("tax", "Token Tax"),
            ("route_permit", "Route Permit"),
            # A07 audit M46-5 (BRU-FLT-01): the BRTA registration certificate
            # could not be recorded at all. It is not in the default mandatory
            # list (cd_vehicle_ext.mandatory_document_types) because no live
            # vehicle has one yet; loading them is a business task.
            ("registration", "Registration Certificate"),
            ("other", "Other"),
        ],
        required=True,
        default="fitness",
    )
    number = fields.Char(string="Document Number")
    valid_from = fields.Date()
    valid_to = fields.Date()
    state = fields.Selection(
        [("valid", "Valid"), ("expired", "Expired")], required=True, default="valid"
    )
    # A07 audit M46-5 (D9): this was a STORED compute that depends on today's
    # date, recomputed only on write, so with no cron a certificate read
    # "valid" for ever after it ended. Non-stored, it is decided at read time;
    # the search method keeps ("is_valid", "=", True) domains working.
    # Valid = state valid AND valid_from <= today <= valid_to: a document with
    # no end date proves nothing about today, so it is not valid.
    is_valid = fields.Boolean(compute="_compute_is_valid", search="_search_is_valid")

    @api.depends("state", "valid_from", "valid_to")
    def _compute_is_valid(self):
        today = dhaka_today(self)
        for rec in self:
            rec.is_valid = rec._fix_covers(today, today)

    def _search_is_valid(self, operator, value):
        if operator != "in":
            return NotImplemented
        today = dhaka_today(self)
        return self._fix_valid_domain(today, today)

    def _fix_covers(self, start, end):
        """True when this document is valid on every day from start to end."""
        self.ensure_one()
        return bool(
            self.state == "valid"
            and self.valid_to
            and self.valid_to >= end
            and (not self.valid_from or self.valid_from <= start)
        )

    @api.model
    def _fix_valid_domain(self, start, end):
        """Domain twin of _fix_covers (the dispatch gate searches with it)."""
        return [
            ("state", "=", "valid"),
            ("valid_to", ">=", end),
            "|",
            ("valid_from", "=", False),
            ("valid_from", "<=", start),
        ]

    def write(self, vals):
        # A07 audit M46-5 (D1): any employee turned an expired fitness
        # certificate valid by writing state='valid' and a new end date, with
        # no evidence. A lapsed document stays lapsed: the renewal is a NEW
        # document with its own number and dates, so the register keeps the
        # history the gate decided on. Superuser code (seeds, data loading,
        # a future expiry cron) stays trusted.
        if not self.env.su and {"state", "valid_from", "valid_to"} & set(vals):
            today = dhaka_today(self)
            for rec in self:
                new_state = vals.get("state", rec.state)
                if new_state != "valid":
                    continue
                new_to = fields.Date.to_date(vals.get("valid_to")) or False
                new_from = fields.Date.to_date(vals.get("valid_from")) or False
                changed = (
                    new_state != rec.state
                    or ("valid_to" in vals and new_to != rec.valid_to)
                    or ("valid_from" in vals and new_from != rec.valid_from)
                )
                if not changed:
                    continue
                lapsed = rec.state == "expired" or bool(rec.valid_to and rec.valid_to < today)
                end = new_to if "valid_to" in vals else rec.valid_to
                if lapsed or (end and end < today):
                    raise UserError(
                        "%s is expired and cannot be made valid again by editing it. "
                        "Record the renewal as a new document with its own number "
                        "and dates." % (rec.name or "This document")
                    )
        return super().write(vals)

    def _fix_guarded_fields(self) -> set:
        # A07 P0 recipe M46-5 (D1): `state` was typed by any employee. It is
        # decided at creation from the dates, and afterwards only moves to
        # expired (action_expire); a renewal is a new document.
        return super()._fix_guarded_fields() | {"state"}

    @api.model_create_multi
    def create(self, vals_list):
        today = dhaka_today(self)
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.vehicle.document") or "VDOC/New"
                )
            if self.env.su:
                continue
            # A07 P0 recipe M46-5 (D4): documents were born state=valid, even
            # with no end date. A user's new document is valid only when it
            # has an end date that is not past; recording one as expired (a
            # lapsed certificate, for the history) is always allowed.
            end = fields.Date.to_date(vals.get("valid_to")) or False
            derived = "valid" if end and end >= today else "expired"
            asked = vals.get("state") or derived
            if asked == "valid" and derived != "valid":
                raise UserError(
                    "A document is recorded as valid only with an end date (Valid To) "
                    "that is not past."
                )
            vals["state"] = asked
        if self.env.su:
            return super().create(vals_list)
        # The state was derived above, so it is set through the guard; the
        # records go back in the caller's own environment, without the token.
        return super(FixVehicleDocument, self._guarded()).create(vals_list).with_env(self.env)

    def action_expire(self):
        """Mark a document expired (lapsed, withdrawn or superseded). One-way:
        a renewal is recorded as a new document."""
        for rec in self:
            if rec.state != "valid":
                raise UserError("%s is already expired." % rec.name)
            rec._guarded().write({"state": "expired"})
        return True


class FixVehicleOffroad(models.Model):
    _name = "fix.vehicle.offroad"
    _description = "Vehicle Off-Road Record"
    _inherit = ["fix.vehicle.lock.mixin"]
    _order = "started_on desc, id desc"

    name = fields.Char(required=True, default="New")
    vehicle_id = fields.Many2one(
        "fleet.vehicle", string="Vehicle", required=True, ondelete="cascade", index=True
    )
    reason = fields.Char(required=True)
    started_on = fields.Date(required=True, default=fields.Date.context_today)
    ended_on = fields.Date()
    state = fields.Selection(
        [("offroad", "Off Road"), ("returned", "Returned to Service")],
        required=True,
        default="offroad",
    )
    # A07 P0 recipe M46-8 (§8.1 "repair complete; re-check passed"): the
    # evidence the return rests on, and who returned it.
    returned_by_id = fields.Many2one("res.users", string="Returned By", readonly=True, copy=False)
    return_check_id = fields.Many2one(
        "fix.vehicle.check",
        string="Re-Check",
        readonly=True,
        copy=False,
        ondelete="restrict",
        help="The passed pre-use check, recorded after the vehicle went off-road, "
        "on which it was returned to service.",
    )

    def _fix_guarded_fields(self) -> set:
        # A07 P0 recipe M46-8 (D1): write(state='returned') and the P03 form
        # (which offered `state` as an input) returned a van to service
        # with no re-check.
        return super()._fix_guarded_fields() | {
            "state",
            "ended_on",
            "returned_by_id",
            "return_check_id",
        }

    def _fix_frozen_fields(self) -> set:
        if self.state == "returned":
            return {"vehicle_id", "reason", "started_on"}
        return set()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.vehicle.offroad") or "VOFF/New"
                )
        return super().create(vals_list)

    def _fix_return_check(self):
        """The passed pre-use check that clears this record: same vehicle,
        dated on or after the off-road start AND recorded after the off-road
        record was opened (so the check that found the defect, or an older
        one, never clears it). Superuser read: the gate decides on facts."""
        self.ensure_one()
        return (
            self.env["fix.vehicle.check"]
            .sudo()
            .search(
                [
                    ("vehicle_id", "=", self.vehicle_id.id),
                    ("passed", "=", True),
                    ("checked_on", ">=", self.started_on),
                    ("create_date", ">=", self.create_date),
                ],
                order="create_date desc, id desc",
                limit=1,
            )
        )

    def action_return(self):
        """Off-road -> returned to service (§8.1). Needs a passed re-check
        recorded after the off-road start, and a second person: the user who
        took the vehicle off the road cannot return it (A07 P0 recipe M46-8;
        live off-road 3 was opened and returned by one user the same day)."""
        for rec in self:
            if rec.state != "offroad":
                raise UserError("Return an off-road vehicle")
            if not self.env.su and rec.create_uid == self.env.user:
                raise UserError(
                    "Segregation of duties: you took %s off the road; another person "
                    "must return it to service." % rec.name
                )
            check = rec._fix_return_check()
            if not check:
                raise UserError(
                    "%s cannot return to service: it needs a passed pre-use check "
                    "recorded after the vehicle went off-road (%s)." % (rec.name, rec.started_on)
                )
            rec._guarded().write(
                {
                    "state": "returned",
                    "ended_on": fields.Date.context_today(self),
                    "returned_by_id": self.env.uid,
                    "return_check_id": check.id,
                }
            )
        return True


class FixVehicleCheck(models.Model):
    _name = "fix.vehicle.check"
    _description = "Vehicle Daily Pre-Use Check"
    # A07 P0 recipe M46-7: a saved check is a record of what was seen on
    # the day; it is never rewritten (a failed brake check was flipped to
    # passed by another user). A new check is recorded instead.
    _inherit = ["fix.vehicle.lock.mixin"]
    _order = "checked_on desc, id desc"

    name = fields.Char(required=True, default="New")
    vehicle_id = fields.Many2one(
        "fleet.vehicle", string="Vehicle", required=True, ondelete="cascade", index=True
    )
    driver_id = fields.Many2one("fix.driver", string="Driver", ondelete="set null")
    checked_on = fields.Date(required=True, default=fields.Date.context_today)
    odometer = fields.Integer(string="Odometer (km)")
    # A07 P0 recipe M46-7 (D4): the four items defaulted to True, so an
    # untouched check was `passed`. Each item must now be answered OK by the
    # checker; an unanswered item counts as not OK and the check fails.
    tyres_ok = fields.Boolean(string="Tyres OK")
    lights_ok = fields.Boolean(string="Lights OK")
    fluids_ok = fields.Boolean(string="Fluids OK")
    brakes_ok = fields.Boolean(string="Brakes OK")
    defects = fields.Text()
    passed = fields.Boolean(string="Passed", compute="_compute_passed", store=True)

    _CHECK_FIELDS = frozenset(
        {
            "vehicle_id",
            "driver_id",
            "checked_on",
            "odometer",
            "tyres_ok",
            "lights_ok",
            "fluids_ok",
            "brakes_ok",
            "defects",
        }
    )

    def _fix_frozen_fields(self) -> set:
        # Saved = frozen; a new (unsaved) check is fully editable.
        return set(self._CHECK_FIELDS) if isinstance(self.id, int) else set()

    @api.depends("tyres_ok", "lights_ok", "fluids_ok", "brakes_ok")
    def _compute_passed(self):
        for rec in self:
            rec.passed = all([rec.tyres_ok, rec.lights_ok, rec.fluids_ok, rec.brakes_ok])

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.vehicle.check") or "VCHK/New"
                )
        return super().create(vals_list)


class FixVehiclePm(models.Model):
    _name = "fix.vehicle.pm"
    _description = "Vehicle PM by Odometer"
    _inherit = ["fix.vehicle.lock.mixin"]
    _order = "scheduled_on desc, id desc"

    name = fields.Char(required=True, default="New")
    vehicle_id = fields.Many2one(
        "fleet.vehicle", string="Vehicle", required=True, ondelete="cascade", index=True
    )
    pm_type = fields.Selection(
        [("service", "Scheduled Service"), ("repair", "Repair"), ("tyres", "Tyres")],
        required=True,
        default="service",
    )
    odometer = fields.Integer(string="Odometer at Service (km)")
    due_odometer = fields.Integer(string="Due Odometer (km)")
    scheduled_on = fields.Date(required=True, default=fields.Date.context_today)
    done_on = fields.Date()
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    cost = fields.Monetary(currency_field="currency_id")
    state = fields.Selection([("open", "Open"), ("done", "Done")], required=True, default="open")
    notes = fields.Char()

    def _fix_guarded_fields(self) -> set:
        # A07 P0 recipe M46-13 (D1): a plain user wrote state=done with a
        # negative cost and no odometer. Done is set only by action_done.
        return super()._fix_guarded_fields() | {"state", "done_on"}

    def _fix_frozen_fields(self) -> set:
        # A completed PM is the service history the cost packs read.
        if self.state == "done":
            return {"vehicle_id", "pm_type", "odometer", "due_odometer", "scheduled_on", "cost"}
        return set()

    @api.constrains("cost", "odometer", "due_odometer")
    def _check_non_negative(self):
        for rec in self:
            if (rec.cost or 0.0) < 0:
                raise ValidationError("A PM cost cannot be negative.")
            if (rec.odometer or 0) < 0 or (rec.due_odometer or 0) < 0:
                raise ValidationError("An odometer reading cannot be negative.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.vehicle.pm") or "VPM/New"
        return super().create(vals_list)

    def action_done(self):
        """Open -> done. FR-FLT-027: completion records the odometer at service
        and the cost (zero is a valid cost, e.g. a warranty service; negative
        is not)."""
        for rec in self:
            if rec.state != "open":
                raise UserError("Complete an open PM job")
            if (rec.odometer or 0) <= 0:
                raise UserError(
                    "Record the odometer at service on %s before completing it." % rec.name
                )
            if (rec.cost or 0.0) < 0:
                raise UserError("A PM cost cannot be negative.")
            rec._guarded().write({"state": "done", "done_on": fields.Date.context_today(self)})
        return True


class FixVehicleFuel(models.Model):
    _name = "fix.vehicle.fuel"
    _description = "Vehicle Fuel Transaction"
    _inherit = ["fix.vehicle.lock.mixin"]
    _order = "filled_on desc, id desc"

    name = fields.Char(required=True, default="New")
    vehicle_id = fields.Many2one(
        "fleet.vehicle", string="Vehicle", required=True, ondelete="cascade", index=True
    )
    driver_id = fields.Many2one("fix.driver", string="Driver", ondelete="set null")
    filled_on = fields.Date(required=True, default=fields.Date.context_today)
    litres = fields.Float(string="Litres", required=True)
    odometer = fields.Integer(string="Odometer (km)", required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(string="Amount", currency_field="currency_id")
    station = fields.Char()
    # A07 P0 recipe M46-9 (FR-FLT-034, BRU-FLT-09/10): the exception rules are
    # computed by the server on every recorded change, never typed. A fill
    # that breaks one is HELD; someone other than its recorder reviews it.
    exception_flags = fields.Char(
        string="Exception Codes",
        readonly=True,
        copy=False,
        help="Comma-separated keys of the exception rules this fill breaks.",
    )
    exception_summary = fields.Char(string="Exceptions", compute="_compute_exception_summary")
    review_state = fields.Selection(
        [
            ("none", "No Exception"),
            ("held", "Held for Review"),
            ("cleared", "Reviewed: Cleared"),
            ("rejected", "Reviewed: Rejected"),
        ],
        string="Review",
        required=True,
        default="none",
        readonly=True,
        copy=False,
        index=True,
    )
    reviewed_by_id = fields.Many2one("res.users", string="Reviewed By", readonly=True, copy=False)
    reviewed_on = fields.Datetime(string="Reviewed On", readonly=True, copy=False)
    review_note = fields.Char(string="Review Note", readonly=True, copy=False)

    _litres_positive = models.Constraint("CHECK (litres > 0)", "Fuel litres must be positive")

    # What a recorded fill IS. Re-checked against the rules when changed.
    _FILL_FIELDS = frozenset(
        {"vehicle_id", "driver_id", "filled_on", "litres", "odometer", "amount"}
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "exception_flags",
            "review_state",
            "reviewed_by_id",
            "reviewed_on",
            "review_note",
        }

    def _fix_frozen_fields(self) -> set:
        if self.review_state in ("cleared", "rejected"):
            # Reviewed: the reviewer signed off these figures (M46-9).
            return set(self._FILL_FIELDS)
        if isinstance(self.id, int) and self.create_uid and self.create_uid != self.env.user:
            # M46-9 [E 44]: another user raised a recorded amount 4,500 ->
            # 99,999. Only the recorder corrects their own fill, and the
            # correction is re-checked against the rules.
            return {"amount", "litres", "odometer"}
        return set()

    @api.depends("exception_flags")
    def _compute_exception_summary(self):
        for rec in self:
            codes = [c for c in (rec.exception_flags or "").split(",") if c]
            rec.exception_summary = "; ".join(FUEL_EXCEPTIONS.get(c, c) for c in codes) or False

    @api.constrains("amount")
    def _check_amount(self):
        # M46-9 [E 42]: a negative spend lowered cost per km and Fuel MTD.
        for rec in self:
            if (rec.amount or 0.0) < 0:
                raise ValidationError("A fuel amount cannot be negative.")

    @api.model
    def _fix_tank_capacity(self) -> float:
        raw = self.env["ir.config_parameter"].sudo().get_param(TANK_CAPACITY_PARAM)
        try:
            value = float(raw) if raw not in (None, False, "") else TANK_CAPACITY_DEFAULT
        except (TypeError, ValueError):
            _logger.warning(
                "%s is not a number: %r; using %s", TANK_CAPACITY_PARAM, raw, TANK_CAPACITY_DEFAULT
            )
            value = TANK_CAPACITY_DEFAULT
        return value if value > 0 else TANK_CAPACITY_DEFAULT

    def _fix_exceptions(self) -> list:
        """The FR-FLT-034 rules this fill breaks (keys of FUEL_EXCEPTIONS).

        Reads run as superuser: a rule decides on every fill of the vehicle,
        not only those the recorder can see. A rejected fill is not an
        accepted reading, so it is neither a previous fill nor a duplicate."""
        self.ensure_one()
        Fuel = self.sudo().with_context(active_test=False)
        others = [
            ("vehicle_id", "=", self.vehicle_id.id),
            ("id", "!=", self.id),
            ("review_state", "!=", "rejected"),
        ]
        flags = []
        previous = Fuel.search(
            [
                *others,
                "|",
                ("filled_on", "<", self.filled_on),
                "&",
                ("filled_on", "=", self.filled_on),
                ("id", "<", self.id),
            ],
            order="filled_on desc, id desc",
            limit=1,
        )
        if previous and self.odometer < previous.odometer:
            flags.append("odometer_back")
        if self.litres > self._fix_tank_capacity():
            flags.append("over_capacity")
        same_day = Fuel.search([*others, ("filled_on", "=", self.filled_on)])
        if any(abs(f.litres - self.litres) < 0.005 for f in same_day):
            flags.append("duplicate")
        offroad = (
            self.env["fix.vehicle.offroad"]
            .sudo()
            .search_count(
                [
                    ("vehicle_id", "=", self.vehicle_id.id),
                    ("started_on", "<=", self.filled_on),
                    "|",
                    ("state", "=", "offroad"),
                    ("ended_on", ">", self.filled_on),
                ]
            )
        )
        if offroad:
            flags.append("offroad")
        return flags

    def _fix_apply_exceptions(self):
        """Store the rules each fill breaks; a breach holds the fill. A held
        fill stays held until reviewed, even if a correction clears the
        breach: the recorder cannot edit a fill out of its own review."""
        for rec in self:
            if rec.review_state in ("cleared", "rejected"):
                continue
            flags = rec._fix_exceptions()
            vals = {"exception_flags": ",".join(flags) or False}
            if flags and rec.review_state == "none":
                vals["review_state"] = "held"
            rec._guarded().write(vals)

    @staticmethod
    def _fix_missing_fill_facts(vals):
        missing = []
        if not vals.get("driver_id"):
            missing.append("the driver")
        if not (vals.get("amount") or 0.0) > 0:
            missing.append("the amount paid")
        return missing

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.vehicle.fuel") or "VFUEL/New"
                )
            # BRU-FLT-08 [E 41]: every fill names the driver and the amount.
            # Users only: superuser data loading (and the legacy rows that
            # carry neither) stays loadable.
            missing = [] if self.env.su else self._fix_missing_fill_facts(vals)
            if missing:
                raise UserError("A fuel transaction must record %s." % " and ".join(missing))
        recs = super().create(vals_list)
        recs._fix_apply_exceptions()
        return recs

    def write(self, vals):
        if not self.env.su and {"driver_id", "amount"} & set(vals):
            for rec in self:
                missing = self._fix_missing_fill_facts(
                    {
                        "driver_id": vals.get("driver_id", rec.driver_id.id),
                        "amount": vals.get("amount", rec.amount),
                    }
                )
                if missing:
                    raise UserError("A fuel transaction must record %s." % " and ".join(missing))
        res = super().write(vals)
        if self._FILL_FIELDS & set(vals):
            self._fix_apply_exceptions()
        return res

    def _fix_review(self, decision, note):
        for rec in self:
            if rec.review_state != "held":
                raise UserError("%s is not held for review." % rec.name)
            # §13 SoD: "the person who records a fuel transaction may not
            # approve its exception review".
            if not self.env.su and rec.create_uid == self.env.user:
                raise UserError(
                    "Segregation of duties: you recorded %s; another person must "
                    "review its exception." % rec.name
                )
            rec._guarded().write(
                {
                    "review_state": decision,
                    "reviewed_by_id": self.env.uid,
                    "reviewed_on": fields.Datetime.now(),
                    "review_note": note,
                }
            )
        return True

    def action_clear_exception(self, note=None):
        """Held -> cleared: the reviewer accepts the fill as genuine."""
        return self._fix_review("cleared", _reason(note, "clearing the fuel exception"))

    def action_reject_fill(self, reason=None):
        """Held -> rejected: the fill is not accepted (not a reading, not a cost)."""
        return self._fix_review("rejected", _reason(reason, "rejecting the fuel transaction"))


class FixVehicleTelemetry(models.Model):
    _name = "fix.vehicle.telemetry"
    _description = "Vehicle Telemetry Snapshot"
    _order = "last_ping desc, id desc"

    name = fields.Char(required=True, default="New")
    vehicle_id = fields.Many2one(
        "fleet.vehicle", string="Vehicle", required=True, ondelete="cascade", index=True
    )
    device_ref = fields.Char(string="Telematics Device")
    last_ping = fields.Datetime(string="Last Ping")
    odometer = fields.Integer(string="Odometer (km)")
    fuel_level_pct = fields.Integer(string="Fuel Level %", default=100)
    state = fields.Selection(
        [("online", "Online"), ("stale", "Stale"), ("offline", "Offline")],
        required=True,
        default="online",
    )

    _fuel_range = models.Constraint(
        "CHECK (fuel_level_pct >= 0 AND fuel_level_pct <= 100)",
        "Fuel level is a 0–100 percentage",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.vehicle.telemetry") or "VTEL/New"
                )
        return super().create(vals_list)


class FixApprovalMatrixM46(models.Model):
    """M46's decision domain in the approval register (A07 P0 recipe)."""

    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[("vehicle_accident_settlement", "Vehicle Accident Claim Settlement")],
        ondelete={"vehicle_accident_settlement": "cascade"},
    )


class FixVehicleAccident(models.Model):
    _name = "fix.vehicle.accident"
    _description = "Vehicle Accident / Incident"
    # A07 P0 recipe M46-10: the claim settlement is a DOFA decision routed by
    # the M63 engine, and the chatter keeps the trail of claim, approval and
    # close. fix.dofa.mixin already carries fix.approvable.mixin (the engine
    # extends it, as on fix.campaign); naming the approvable mixin here as
    # well gives Python no consistent method order.
    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
        "fix.dofa.mixin",
        "fix.vehicle.lock.mixin",
    ]
    _order = "occurred_on desc, id desc"

    _approval_domain = "vehicle_accident_settlement"
    _approval_apply_method = "action_dofa_approve"
    _approval_routed = True

    name = fields.Char(required=True, default="New")
    vehicle_id = fields.Many2one(
        "fleet.vehicle", string="Vehicle", required=True, ondelete="cascade", index=True
    )
    driver_id = fields.Many2one("fix.driver", string="Driver", ondelete="set null")
    occurred_on = fields.Date(required=True, default=fields.Date.context_today)
    description = fields.Text(required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    damage_cost = fields.Monetary(currency_field="currency_id")
    claim_ref = fields.Char(string="Insurance Claim Ref")
    settlement_amount = fields.Monetary(
        string="Settlement Amount",
        currency_field="currency_id",
        copy=False,
        tracking=True,
        help="The claim settlement the closer records. Above Tier 0 it needs a "
        "DOFA approval routed from the approver's inbox, and the approval "
        "covers this exact figure: changing it afterwards withdraws it.",
    )
    state = fields.Selection(
        [("reported", "Reported"), ("claimed", "Claim Filed"), ("closed", "Closed")],
        required=True,
        default="reported",
        tracking=True,
    )
    closed_by_id = fields.Many2one("res.users", string="Closed By", readonly=True, copy=False)
    closed_on = fields.Date(string="Closed On", readonly=True, copy=False)

    # ---- DOFA (fix.dofa.mixin) --------------------------------------------
    def _dofa_thresholds(self):
        return ACCIDENT_SETTLEMENT_DOFA_THRESHOLDS

    def _dofa_amount(self) -> float:
        self.ensure_one()
        return self.settlement_amount or 0.0

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "BDT %.2f (accident claim settlement)" % self._dofa_amount()

    @api.depends("settlement_amount")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    # ---- guard and state lock ---------------------------------------------
    def _fix_guarded_fields(self) -> set:
        # A07 P0 recipe M46-10 (D1): `reported -> closed` was set by write.
        return super()._fix_guarded_fields() | {"state", "closed_by_id", "closed_on"}

    def _fix_frozen_fields(self) -> set:
        if self.state == "closed":
            # [E 49]: a closed incident's damage cost was edited 50,000 -> 1.
            return {
                "vehicle_id",
                "driver_id",
                "occurred_on",
                "description",
                "damage_cost",
                "claim_ref",
                "settlement_amount",
                "dofa_justification",
            }
        if self.state == "claimed":
            # The claim was filed on this vehicle under this reference.
            return {"vehicle_id", "claim_ref"}
        return set()

    @api.constrains("damage_cost", "settlement_amount")
    def _check_amounts(self):
        for rec in self:
            if (rec.damage_cost or 0.0) < 0 or (rec.settlement_amount or 0.0) < 0:
                raise ValidationError("Accident damage and settlement amounts cannot be negative.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.vehicle.accident") or "VACC/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        # The pin: an approval covers the settlement that was signed off. The
        # DOFA mixin withdraws it when the figure RISES; a settlement accepted
        # below the approved figure is also a different decision, so any
        # change withdraws it and the closer must request approval again.
        approved = self.filtered("dofa_approved") if "settlement_amount" in vals else self.browse()
        before = {rec.id: rec.settlement_amount or 0.0 for rec in approved}
        res = super().write(vals)
        for rec in approved.filtered("dofa_approved"):
            if abs((rec.settlement_amount or 0.0) - before[rec.id]) > 0.005:
                rec._dofa_void_approval(
                    "the settlement changed from %.2f to %.2f after approval; "
                    "request approval again." % (before[rec.id], rec.settlement_amount or 0.0)
                )
        return res

    # ---- transitions --------------------------------------------------------
    def action_claim(self, claim_ref=None):
        """Reported -> claim filed. FR-FLT-042: a claim is filed with the
        insurer's claim reference (given here or already on the record)."""
        for rec in self:
            if rec.state != "reported":
                raise UserError("File a claim for a reported accident")
            ref = ((claim_ref if isinstance(claim_ref, str) else "") or rec.claim_ref or "").strip()
            if not ref:
                raise UserError(
                    "File the claim for %s with the insurer's claim reference." % rec.name
                )
            rec._guarded().write({"state": "claimed", "claim_ref": ref})
            rec.message_post(body="Claim filed by %s, reference %s." % (self.env.user.name, ref))
        return True

    def action_request_approval(self, justification=None):
        # The settlement is approved on a filed claim, for a stated figure.
        for rec in self:
            if rec.state != "claimed":
                raise UserError("Request settlement approval on a filed claim.")
        return super().action_request_approval(justification=justification)

    def action_close(self, settlement=None):
        """Claim filed -> closed (§13 SoD, M46-10).

        The closer states the settled amount (0 for a claim the insurer
        declined) and is not the person who reported the accident. A
        settlement above Tier 0 must carry a DOFA approval of that figure,
        granted from the approver's inbox."""
        for rec in self:
            if rec.state != "claimed":
                raise UserError("Close a claimed accident")
            # 0 is a real answer (a declined claim); only "nothing" is missing
            if settlement is None or settlement is False or not str(settlement).strip():
                raise UserError("State the settled amount to close %s (0 if declined)." % rec.name)
            try:
                amount = float(str(settlement).replace(",", "").strip())
            except ValueError as exc:
                raise UserError("The settled amount must be a number.") from exc
            if amount < 0:
                raise UserError("The settled amount cannot be negative.")
            if not self.env.su and rec.create_uid == self.env.user:
                raise UserError(
                    "Segregation of duties: you reported %s; another person must close "
                    "its claim." % rec.name
                )
            if abs(amount - (rec.settlement_amount or 0.0)) > 0.005:
                rec.write({"settlement_amount": amount})
            rec._dofa_assert_approved("Closing the claim")
            rec._guarded().write(
                {
                    "state": "closed",
                    "closed_by_id": self.env.uid,
                    "closed_on": fields.Date.context_today(self),
                }
            )
            rec.message_post(
                body="Claim closed by %s with a settlement of %s."
                % (self.env.user.name, rec._dofa_amount_label())
            )
        return True
