# fix_vehicle — M46: fleet extension + dispatch vehicle assignment (P08-M08).
from odoo import api, fields, models
from odoo.exceptions import ValidationError

from libs.py.fix_events import publish

from .fix_vehicle_ops import dhaka_today

# A07 audit (2026-11-03) M46-2/M46-3: which statutory documents a vehicle must
# hold, valid today, before it may be dispatched. A comma-separated list of
# fix.vehicle.document doc_type keys. `registration` exists as a type but is
# not in the default: no live vehicle has one recorded yet, and loading them
# is a business task. "tax_token" is accepted for the Token Tax key `tax`.
MANDATORY_DOCS_PARAM = "cd_vehicle_ext.mandatory_document_types"
MANDATORY_DOCS_DEFAULT = "fitness,insurance,tax"
_DOC_TYPE_ALIASES = {"tax_token": "tax"}

# BRU-FLT-07: a passed pre-use check before the first dispatch of the day.
# Off by default: no live vehicle records a daily check yet, so switching it
# on would stop every dispatch on deploy. A business decision.
PREUSE_PARAM = "cd_vehicle_ext.require_passed_preuse_check"

_OPEN_ACCIDENT_STATES = ("reported", "claimed")


def param_on(env, key):
    """An ir.config_parameter read as a boolean switch (default off)."""
    value = env["ir.config_parameter"].sudo().get_param(key, "False")
    return str(value).strip().lower() in ("1", "true", "yes", "on")


class FleetVehicleCdExt(models.Model):
    _inherit = "fleet.vehicle"

    branch_id = fields.Many2one("fix.branch", string="Branch")
    # NOT driver_employee_id: hr_fleet defines that as a computed field
    fix_driver_id = fields.Many2one("fix.driver", string="Assigned Driver")
    # A07 audit M46-3: the two header dates are INFORMATION ONLY. The gate
    # used to read them, so a fleet officer typing a future insurance date
    # made an uninsured van dispatchable (BRU-FLT-03: no override at any
    # level). Dispatch is decided from the document register below.
    fitness_expiry = fields.Date(string="Fitness Expiry (header, information)")
    insurance_expiry = fields.Date(string="Insurance Expiry (header, information)")
    document_ids = fields.One2many("fix.vehicle.document", "vehicle_id", string="Documents")
    compliance_ok = fields.Boolean(
        compute="_compute_compliance",
        string="Compliance OK",
        help="Every mandatory statutory document is in the register and valid today.",
    )
    dispatch_blockers = fields.Text(
        compute="_compute_dispatch_blockers",
        string="Dispatch Blockers",
        help="Why the dispatch gate would refuse this vehicle today (empty = dispatchable).",
    )

    @api.depends(
        "document_ids.state",
        "document_ids.doc_type",
        "document_ids.valid_from",
        "document_ids.valid_to",
    )
    def _compute_compliance(self):
        missing = self._fix_missing_documents(dhaka_today(self), dhaka_today(self))
        for rec in self:
            rec.compliance_ok = not missing.get(rec.id)

    def _compute_dispatch_blockers(self):
        blockers = self._fix_dispatch_blockers()
        for rec in self:
            rec.dispatch_blockers = "; ".join(blockers.get(rec.id, [])) or False

    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

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

    def _fix_missing_documents(self, start, end):
        """{vehicle id: [doc types with no document valid from start to end]}.

        An unknown type in the parameter can never be satisfied, so a typo
        fails closed and the refusal names it."""
        types = self._fix_mandatory_document_types()
        if not self.ids or not types:
            return {}
        Doc = self.env["fix.vehicle.document"].sudo()
        held = {
            (d.vehicle_id.id, d.doc_type)
            for d in Doc.search(
                [
                    ("vehicle_id", "in", self.ids),
                    ("doc_type", "in", types),
                    *Doc._fix_valid_domain(start, end),
                ]
            )
        }
        return {
            vid: missing
            for vid in self.ids
            if (missing := [t for t in types if (vid, t) not in held])
        }

    def _fix_dispatch_blockers(self, driver=None, day=None):
        """{vehicle id: [reason, ...]} for every vehicle the gate refuses.

        A07 audit M46-2: the gate read only the two header dates. It now
        refuses a vehicle unless, on the Dhaka date:
          - each mandatory document type is valid from today through `day`
            (so a van is not booked for a day its insurance has ended);
          - it has no open off-road record and no open (reported or claimed)
            accident (BRU-FLT-02, BRU-FLT-13);
          - no pre-use check failed today (BRU-FLT-04); with the
            PREUSE_PARAM switch on, a passed check today is also required
            for a job today (BRU-FLT-07);
          - its driver (`driver`, else the vehicle's assigned driver) is
            active and holds a licence whose recorded expiry is not past on
            `day` (BRU-FLT-05). Licence CLASS is not matched: there is no
            vehicle class field to match it to.
        Reads run as superuser on purpose: a gate that the caller passes
        because their record rules hide the off-road record fails open."""
        if not self:
            return {}
        today = dhaka_today(self)
        day = fields.Date.to_date(day) or today
        until = max(day, today)
        labels = dict(self.env["fix.vehicle.document"]._fields["doc_type"].selection)
        out = {vid: [] for vid in self.ids}

        for vid, missing in self._fix_missing_documents(today, until).items():
            out[vid].extend(
                "no valid %s document in the register" % labels.get(t, t) for t in missing
            )

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
            if not drv:
                continue
            if drv.state != "active":
                out[vehicle.id].append("driver %s is %s" % (drv.name, drv.state))
            if not drv.license_expiry:
                out[vehicle.id].append("driver %s has no licence expiry recorded" % drv.name)
            elif drv.license_expiry < until:
                out[vehicle.id].append(
                    "driver %s's licence expired on %s" % (drv.name, drv.license_expiry)
                )
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
