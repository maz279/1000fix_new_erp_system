# fix_vehicle — M46: fleet extension + dispatch vehicle assignment (P08-M08).
import re

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from .fix_vehicle_ops import (
    LICENCE_CLASS_PARAM,
    LICENCE_CLASSES,
    LICENCE_COVERS,
    dhaka_today,
    param_on,
)

# A07 audit (2026-11-03) M46-2/M46-3: which statutory documents a vehicle must
# hold, valid today, before it may be dispatched. A comma-separated list of
# fix.vehicle.document doc_type keys. `registration` exists as a type but is
# not in the default: no live vehicle has one recorded yet, and loading them
# is a business task. "tax_token" is accepted for the Token Tax key `tax`.
# The route permit is decision B3 (Road Transport Act s.28 vs s.31): add
# `route_permit` here once counsel confirms the vans need one.
MANDATORY_DOCS_PARAM = "cd_vehicle_ext.mandatory_document_types"
MANDATORY_DOCS_DEFAULT = "fitness,insurance,tax"
_DOC_TYPE_ALIASES = {"tax_token": "tax"}

# BRU-FLT-07: a passed pre-use check before the first dispatch of the day.
# Off by default: no live vehicle records a daily check yet, so switching it
# on would stop every dispatch on deploy. A business decision.
PREUSE_PARAM = "cd_vehicle_ext.require_passed_preuse_check"

_OPEN_ACCIDENT_STATES = ("reported", "claimed")

# The header dates mirror these document types (A07 P1 M46-3).
_HEADER_DOCS = {"fitness_expiry": "fitness", "insurance_expiry": "insurance"}


def _plate_key(plate):
    """A licence plate compared without case, spaces or punctuation."""
    return re.sub(r"[\W_]+", "", plate or "").casefold()


class FleetVehicleCdExt(models.Model):
    _inherit = "fleet.vehicle"

    branch_id = fields.Many2one("fix.branch", string="Branch")
    # NOT driver_employee_id: hr_fleet defines that as a computed field
    fix_driver_id = fields.Many2one("fix.driver", string="Assigned Driver")
    # A07 audit M46-3 / A07 P1 [probes 10, 24]: the two header dates were
    # typed, so a fleet officer typing a future insurance date "renewed" an
    # uninsured van (BRU-FLT-03: no override at any level) and the header and
    # the register were two unlinked truths. They are now READ from the
    # register (the latest recorded document of each type) and refused as
    # input; dispatch is decided from the register itself.
    fitness_expiry = fields.Date(
        string="Fitness Expiry (from the register)",
        compute="_compute_header_dates",
        store=True,
        readonly=True,
    )
    insurance_expiry = fields.Date(
        string="Insurance Expiry (from the register)",
        compute="_compute_header_dates",
        store=True,
        readonly=True,
    )
    document_ids = fields.One2many("fix.vehicle.document", "vehicle_id", string="Documents")
    compliance_ok = fields.Boolean(
        compute="_compute_compliance",
        string="Compliance OK",
        help="Every mandatory statutory document is in the register, current, "
        "evidenced and valid today.",
    )
    dispatch_blockers = fields.Text(
        compute="_compute_dispatch_blockers",
        string="Dispatch Blockers",
        help="Why the dispatch gate would refuse this vehicle today (empty = dispatchable).",
    )
    # A07 P1 M46-6 (BRU-FLT-05) [probe 17]: the licence class the vehicle
    # needs. From the model type (bike = motorcycle, car/van = light); a Fleet
    # Officer raises it for a medium or heavy vehicle.
    fix_licence_class_required = fields.Selection(
        LICENCE_CLASSES,
        string="Licence Class Required",
        compute="_compute_licence_class_required",
        store=True,
        readonly=False,
    )
    # A07 P1 M46-9 (FR-FLT-034): the tank this vehicle has; empty = the
    # fleet-wide ceiling (cd_vehicle_ext.fuel_tank_capacity_litres).
    fix_tank_capacity_l = fields.Float(string="Fuel Tank Capacity (L)")
    # BRU-FLT-19: the latest telemetry snapshot is not online.
    fix_position_unknown = fields.Boolean(
        compute="_compute_position_unknown",
        string="Position Unknown",
        help="A telematics device is recorded and its latest snapshot is not online "
        "(silent beyond the configured interval).",
    )

    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    @api.depends("document_ids.doc_type", "document_ids.valid_to")
    def _compute_header_dates(self):
        for rec in self:
            for fname, doc_type in _HEADER_DOCS.items():
                docs = rec.document_ids.filtered(lambda d, t=doc_type: d.doc_type == t)
                latest = max(docs, key=lambda d: d._origin.id or d.id or 0) if docs else None
                rec[fname] = latest.valid_to if latest else False

    @api.depends("model_id.vehicle_type")
    def _compute_licence_class_required(self):
        for rec in self:
            if rec.model_id.vehicle_type == "bike":
                rec.fix_licence_class_required = "motorcycle"
            elif (
                not rec.fix_licence_class_required or rec.fix_licence_class_required == "motorcycle"
            ):
                rec.fix_licence_class_required = "light"

    def _compute_position_unknown(self):
        Tel = self.env["fix.vehicle.telemetry"].sudo()
        for rec in self:
            latest = Tel.search(
                [("vehicle_id", "=", rec.id)], order="last_ping desc, id desc", limit=1
            )
            rec.fix_position_unknown = bool(latest and latest.state != "online")

    @api.depends(
        "document_ids.state",
        "document_ids.doc_type",
        "document_ids.valid_from",
        "document_ids.valid_to",
        "document_ids.has_evidence",
    )
    def _compute_compliance(self):
        today = dhaka_today(self)
        missing = self._fix_missing_documents(today, today)
        for rec in self:
            rec.compliance_ok = not missing.get(rec.id)

    def _compute_dispatch_blockers(self):
        blockers = self._fix_dispatch_blockers()
        for rec in self:
            rec.dispatch_blockers = "; ".join(blockers.get(rec.id, [])) or False

    # ------------------------------------------------------------ register
    @api.constrains("license_plate", "active")
    def _check_unique_plate(self):
        """A07 P1 [probe 61]: one registration number, one vehicle (live
        vehicles 6 and 7 shared `E2E-GA-11-9999`). Compared without case,
        spaces or punctuation, across companies (a plate is national), among
        active vehicles: a disposed, archived vehicle keeps its history."""
        Vehicle = self.sudo().with_context(active_test=True)
        for rec in self.filtered(lambda r: r.active and _plate_key(r.license_plate)):
            key = _plate_key(rec.license_plate)
            others = Vehicle.search([("id", "!=", rec.id), ("license_plate", "!=", False)])
            clash = others.filtered(lambda v, k=key: _plate_key(v.license_plate) == k)
            if clash:
                raise ValidationError(
                    "Licence plate %s is already registered to %s."
                    % (rec.license_plate, clash[0].name or clash[0].license_plate)
                )

    @api.model_create_multi
    def create(self, vals_list):
        # A07 P1 M46-3: a new vehicle's header dates come from its documents.
        if not self.env.su:
            typed = sorted({f for vals in vals_list for f in _HEADER_DOCS if vals.get(f)})
            if typed:
                self._fix_refuse_typed_header(typed)
        return super().create(vals_list)

    def _fix_refuse_typed_header(self, names):
        raise UserError(
            "%s comes from the statutory document register: record the certificate "
            "(with its scan) as a vehicle document instead."
            % ", ".join(self._fields[f].string for f in names)
        )

    def write(self, vals):
        # A07 P1 M46-3 (BRU-FLT-03) [probe 10]: the header dates are the
        # register's; typing one is refused (superuser data repair aside).
        if not self.env.su:
            typed = [
                f
                for f in _HEADER_DOCS
                if f in vals
                and any(
                    (fields.Date.to_date(vals[f]) or False) != (rec[f] or False) for rec in self
                )
            ]
            if typed:
                self._fix_refuse_typed_header(typed)
        return super().write(vals)

    @api.model
    def _fix_recompute_header_dates(self):
        """Upgrade hook (data/fix_vehicle_upgrade.xml): the header dates were
        typed columns before A07 P1; recompute every vehicle from its register
        (a vehicle with no document then shows no date, which is the truth)."""
        vehicles = self.sudo().with_context(active_test=False).search([])
        for fname in _HEADER_DOCS:
            self.env.add_to_compute(self._fields[fname], vehicles)
        vehicles.flush_recordset(list(_HEADER_DOCS))
        return True

    def _fix_last_odometer(self) -> int:
        """The highest accepted odometer reading recorded for this vehicle
        (fleet log, accepted fills, checks, completed services, telemetry)."""
        self.ensure_one()
        env = self.env(su=True)
        readings = [int(self.sudo().odometer or 0)]
        for model, domain in (
            ("fix.vehicle.fuel", [("review_state", "in", ("none", "cleared"))]),
            ("fix.vehicle.check", []),
            ("fix.vehicle.pm", [("state", "=", "done")]),
            ("fix.vehicle.telemetry", []),
        ):
            rec = env[model].search(
                [("vehicle_id", "=", self.id), ("odometer", ">", 0), *domain],
                order="odometer desc",
                limit=1,
            )
            readings.append(rec.odometer if rec else 0)
        return max(readings)

    def _fix_take_offroad(self, cause, reason, raised_by=None, **links):
        """The system takes each vehicle off the road (A07 P1: a failed check,
        a reported accident, a lapsed document, an overdue service). One open
        record per vehicle and cause; the source record is linked. Superuser:
        the reporter may not hold the off-road rights, and the off-road record
        must exist whatever their record rules show."""
        Off = self.env["fix.vehicle.offroad"].sudo()
        created = Off.browse()
        for vehicle in self:
            if Off.search_count(
                [("vehicle_id", "=", vehicle.id), ("state", "=", "offroad"), ("cause", "=", cause)]
            ):
                continue
            created |= Off.create(
                {
                    "vehicle_id": vehicle.id,
                    "cause": cause,
                    "reason": reason,
                    "raised_by_id": raised_by.id if raised_by else False,
                    **links,
                }
            )
        return created

    # ------------------------------------------------------------ the gate
    @api.model
    def _fix_mandatory_document_types(self):
        raw = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(MANDATORY_DOCS_PARAM, MANDATORY_DOCS_DEFAULT)
        )
        types = []
        for item in (raw or "").split(","):
            key = _DOC_TYPE_ALIASES.get(item.strip(), item.strip())
            if key and key not in types:
                types.append(key)
        return types

    def _fix_document_problems(self, start, end, lapsed_only=False):
        """{vehicle id: [reason, ...]} for each mandatory document type that
        is not covered on `start` and on `end`.

        The document read is the CURRENT one of its type on that day (the
        latest recorded in force: fix.vehicle.document.is_current), so a lapse
        or a cancellation recorded after a still-dated certificate decides
        (A07 P1 [probes 06, 24]). Covered = state valid, dated over the day,
        and evidenced (A07 P1 [probe 23]). An unknown type in the parameter
        can never be satisfied, so a typo fails closed and the refusal names
        it. With `lapsed_only`, only a current document that lapsed counts
        (the midnight off-road job); a missing document is the gate's."""
        types = self._fix_mandatory_document_types()
        if not self.ids or not types:
            return {}
        Doc = self.env["fix.vehicle.document"].sudo()
        labels = dict(Doc._fields["doc_type"].selection)
        out = {}
        for day in sorted({fields.Date.to_date(start), fields.Date.to_date(end)}):
            current = Doc._fix_current_map(self.ids, day, types)
            for vid in self.ids:
                for doc_type in types:
                    doc = current.get((vid, doc_type))
                    if not doc:
                        if lapsed_only:
                            continue
                        reason = "no valid %s document in the register" % labels.get(
                            doc_type, doc_type
                        )
                    else:
                        reason = doc._fix_problem(day)
                        if (
                            reason
                            and lapsed_only
                            and not (doc.state != "valid" or (doc.valid_to and doc.valid_to < day))
                        ):
                            continue
                    if reason and reason not in out.setdefault(vid, []):
                        out[vid].append(reason)
        return {vid: reasons for vid, reasons in out.items() if reasons}

    def _fix_missing_documents(self, start, end):
        """{vehicle id: [reason, ...]} (kept for callers of the P0 name)."""
        return self._fix_document_problems(start, end)

    def _fix_driver_problems(self, drv, until):
        """Why `drv` may not drive this vehicle on `until` (a list)."""
        self.ensure_one()
        out = []
        if drv.state != "active":
            out.append("driver %s is %s" % (drv.name, drv.state))
        if not drv.license_expiry:
            out.append("driver %s has no licence expiry recorded" % drv.name)
        elif drv.license_expiry < until:
            out.append("driver %s's licence expired on %s" % (drv.name, drv.license_expiry))
        # A07 P1 M46-6 (BRU-FLT-05, AUT-FLT-06) [probe 17]: the licence class
        # must cover the vehicle. A class not recorded in BRTA terms (live
        # rows say "professional" or nothing) blocks only with
        # cd_vehicle_ext.require_licence_class on (off: deploy-safe, B2).
        need = self.fix_licence_class_required
        held = drv._fix_licence_classes()
        labels = dict(LICENCE_CLASSES)
        if need and held:
            if not any(need in LICENCE_COVERS[c] for c in held):
                out.append(
                    "driver %s's licence (%s) does not cover a %s"
                    % (drv.name, drv.license_class, labels[need].lower())
                )
        elif need and param_on(self.env, LICENCE_CLASS_PARAM):
            out.append("driver %s's licence class is not recorded in BRTA terms" % drv.name)
        return out

    def _fix_dispatch_blockers(self, driver=None, day=None):
        """{vehicle id: [reason, ...]} for every vehicle the gate refuses.

        A07 audit M46-2: the gate read only the two header dates. It now
        refuses a vehicle unless, on the Dhaka date:
          - each mandatory document type's current document is valid, with
            its evidence, today and on `day` (so a van is not booked for a
            day its insurance has ended);
          - it has no open off-road record and no open (reported or claimed)
            accident (BRU-FLT-02, BRU-FLT-13);
          - no pre-use check failed today (BRU-FLT-04); with the
            PREUSE_PARAM switch on, a passed check today is also required
            for a job today (BRU-FLT-07);
          - its driver (`driver`, else the vehicle's assigned driver) is
            active, holds a licence whose recorded expiry is not past on
            `day`, and whose class covers the vehicle (BRU-FLT-05).
        Reads run as superuser on purpose: a gate that the caller passes
        because their record rules hide the off-road record fails open."""
        if not self:
            return {}
        today = dhaka_today(self)
        day = fields.Date.to_date(day) or today
        until = max(day, today)
        out = {vid: [] for vid in self.ids}

        for vid, problems in self._fix_document_problems(today, until).items():
            out[vid].extend(problems)

        sudo = self.env(su=True)
        for rec in sudo["fix.vehicle.offroad"].search(
            [("vehicle_id", "in", self.ids), ("state", "=", "offroad")]
        ):
            out[rec.vehicle_id.id].append("open off-road record %s (%s)" % (rec.name, rec.reason))
        for rec in sudo["fix.vehicle.accident"].search(
            [("vehicle_id", "in", self.ids), ("state", "in", _OPEN_ACCIDENT_STATES)]
        ):
            out[rec.vehicle_id.id].append("open accident %s (%s)" % (rec.name, rec.state))

        checks = sudo["fix.vehicle.check"].search(
            [("vehicle_id", "in", self.ids), ("checked_on", "=", today)]
        )
        for rec in checks.filtered(lambda c: not c.passed):
            out[rec.vehicle_id.id].append(
                "pre-use check %s failed today (%s)" % (rec.name, rec.defects or "defect recorded")
            )
        if day == today and param_on(self.env, PREUSE_PARAM):
            passed = set(checks.filtered("passed").mapped("vehicle_id").ids)
            for vid in self.ids:
                if vid not in passed:
                    out[vid].append("no passed pre-use check today")

        for vehicle in self.sudo():
            drv = driver if driver is not None else vehicle.fix_driver_id
            drv = drv.sudo() if drv else drv
            if drv:
                out[vehicle.id].extend(vehicle._fix_driver_problems(drv, until))
        return {vid: reasons for vid, reasons in out.items() if reasons}

    def _fix_assert_dispatchable(self, driver=None, day=None):
        blockers = self._fix_dispatch_blockers(driver=driver, day=day)
        # sudo: a plain employee may book a van they cannot read (fleet ACL)
        for rec in self.sudo():
            if blockers.get(rec.id):
                raise ValidationError(
                    "Vehicle %s is not dispatchable: %s."
                    % (rec.name or rec.license_plate, "; ".join(blockers[rec.id]))
                )
        return True

    def action_assert_dispatchable(self):
        return self._fix_assert_dispatchable()


class FixVehicleAssignment(models.Model):
    """The W2-deferred dispatch connection, delivered (P08-M08-T04): a
    vehicle on a service day. Overlaps refused — a van cannot be in two
    places."""

    _name = "fix.vehicle.assignment"
    _description = "Vehicle Assignment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    vehicle_id = fields.Many2one("fleet.vehicle", required=True, index=True)
    date = fields.Date(required=True)
    order_id = fields.Many2one("fix.service.order", string="Service Order", ondelete="set null")
    technician_id = fields.Many2one("hr.employee", string="Technician")
    # A07 audit M46-6 (BRU-FLT-06): the accountable driver for the day. When
    # none is given the vehicle's assigned driver is used, so the gate checks
    # the person who will actually drive.
    driver_id = fields.Many2one("fix.driver", string="Driver", index=True, ondelete="restrict")
    # Changing any of these re-runs the gate and the overlap check.
    _GATE_FIELDS = frozenset({"vehicle_id", "date", "driver_id"})

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("driver_id") and vals.get("vehicle_id"):
                vehicle = self.env["fleet.vehicle"].sudo().browse(vals["vehicle_id"])
                if vehicle.fix_driver_id:
                    vals["driver_id"] = vehicle.fix_driver_id.id
        recs = super().create(vals_list)
        recs._fix_check_dispatchable()
        for rec in recs:
            publish(
                self.env,
                "vehicle.assigned",
                "fix.vehicle.assignment",
                rec.id,
                {"vehicle": rec.sudo().vehicle_id.name or "", "date": str(rec.date)},
            )
        return recs

    def write(self, vals):
        # A07 audit M46-4 (D2): write() bypassed both checks, so an assignment
        # made on a compliant van was re-pointed to the uninsured one, or
        # moved onto a day the van was already booked.
        res = super().write(vals)
        if self._GATE_FIELDS & set(vals):
            self._fix_check_dispatchable()
        return res

    def _fix_check_dispatchable(self):
        # sudo reads: a plain employee may book a van they cannot read (fleet
        # ACL); the gate decides on facts, not on what the caller can see.
        for rec in self.sudo():
            rec.vehicle_id._fix_assert_dispatchable(driver=rec.driver_id, day=rec.date)
            # sudo: an overlap in an operating unit the caller cannot read is
            # still an overlap (the van is still in the other place).
            overlaps = self.sudo().search_count(
                [
                    ("vehicle_id", "=", rec.vehicle_id.id),
                    ("date", "=", rec.date),
                    ("id", "!=", rec.id),
                ]
            )
            if overlaps:
                raise ValidationError(
                    "Vehicle %s already assigned on %s — overlaps are refused"
                    % (rec.vehicle_id.name or "vehicle", rec.date)
                )
