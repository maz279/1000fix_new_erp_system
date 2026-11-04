# fix_vehicle_ops — M46: drivers, statutory documents, off-road records, daily
# pre-use checks, PM by odometer, fuel transactions, telematics snapshots and
# accidents. The vehicle register (fleet.vehicle extension) and dispatch
# assignments live in fix_vehicle.py.
import logging
import re
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

_logger = logging.getLogger(__name__)

# A07 P1 (2026-11-04) M46-17 (D7): the roles. Fleet Officer is Odoo fleet's
# own "Officer: Manage all vehicles" group, the group the audit counts as the
# Fleet Officer (spec R15 Logistics Coordinator): a second officer group
# would be a second truth about who may manage the register. Logistics
# Manager is new (security/cd_vehicle_ext_groups.xml) and implies it.
FLEET_OFFICER_GROUP = "fleet.fleet_group_user"
LOGISTICS_MANAGER_GROUP = "cd_vehicle_ext.group_logistics_manager"
ROLE_LABELS = {
    FLEET_OFFICER_GROUP: "Fleet Officer (Fleet: Officer: Manage all vehicles)",
    LOGISTICS_MANAGER_GROUP: "Logistics Manager",
}

# A07 P1 business switches (ir.config_parameter, data/ir_config_parameter.xml).
# Each default is named in the reply as a value the business must confirm (B2).
EVIDENCE_PARAM = "cd_vehicle_ext.require_document_evidence"
LEGACY_EVIDENCE_PARAM = "cd_vehicle_ext.legacy_documents_count_valid"
DOC_ALERT_DAYS_PARAM = "cd_vehicle_ext.document_alert_days"
DOC_ALERT_DAYS_DEFAULT = "60,30,15,7,1"  # FR-FLT-011 / AUT-FLT-01
LICENCE_ALERT_DAYS_PARAM = "cd_vehicle_ext.licence_alert_days"
LICENCE_ALERT_DAYS_DEFAULT = "60,30,15"  # AUT-FLT-04
LICENCE_CLASS_PARAM = "cd_vehicle_ext.require_licence_class"
FUEL_KM_PER_LITRE_PARAM = "cd_vehicle_ext.fuel_max_km_per_litre"
FUEL_KM_PER_LITRE_DEFAULT = 60.0
TELEMATICS_SILENCE_PARAM = "cd_vehicle_ext.telematics_silence_minutes"
TELEMATICS_SILENCE_DEFAULT = 60
PM_TOLERANCE_DAYS_PARAM = "cd_vehicle_ext.pm_overdue_tolerance_days"
PM_TOLERANCE_KM_PARAM = "cd_vehicle_ext.pm_overdue_tolerance_km"
PM_OFFROAD_PARAM = "cd_vehicle_ext.pm_overdue_takes_offroad"

# BRTA driving-licence vehicle classes (Motor Vehicles / Road Transport Act
# 2018 licence categories) and what each covers. A heavy licence covers medium
# and light vehicles; a motorcycle licence covers motorcycles only.
LICENCE_CLASSES = [
    ("motorcycle", "Motorcycle"),
    ("light", "Light Motor Vehicle"),
    ("medium", "Medium Motor Vehicle"),
    ("heavy", "Heavy Motor Vehicle"),
]
LICENCE_COVERS = {
    "motorcycle": {"motorcycle"},
    "light": {"light"},
    "medium": {"light", "medium"},
    "heavy": {"light", "medium", "heavy"},
}
_LICENCE_TOKENS = [
    ("motorcycle", r"motor\s*-?\s*cycle|motor\s*bike|\bbike\b|\bmc\b"),
    ("heavy", r"\bheavy\b|\bhgv\b"),
    ("medium", r"\bmedium\b"),
    ("light", r"\blight\b|\blmv\b"),
]


def licence_classes(text):
    """The BRTA classes a free-text licence class names (a set of keys)."""
    raw = (text or "").lower()
    return {key for key, pattern in _LICENCE_TOKENS if re.search(pattern, raw)}


def param_value(env, key, default=None):
    value = env["ir.config_parameter"].sudo().get_param(key)
    return default if value in (None, False, "") else value


def param_on(env, key, default=False):
    """An ir.config_parameter read as a boolean switch."""
    value = param_value(env, key, "True" if default else "False")
    return str(value).strip().lower() in ("1", "true", "yes", "on")


def param_float(env, key, default):
    raw = param_value(env, key, default)
    try:
        value = float(raw)
    except (TypeError, ValueError):
        _logger.warning("%s is not a number: %r; using %s", key, raw, default)
        return float(default)
    return value if value >= 0 else float(default)


def param_days(env, key, default):
    """A comma-separated list of day counts, largest first."""
    out = set()
    for item in str(param_value(env, key, default)).split(","):
        try:
            out.add(int(item.strip()))
        except ValueError:
            continue
    return sorted((d for d in out if d >= 0), reverse=True)


def require_role(env, xmlid, what):
    """Refuse `what` unless the user holds the role (superuser is trusted)."""
    if env.su or env.user.has_group(xmlid):
        return
    label = ROLE_LABELS.get(xmlid) or xmlid
    raise AccessError("%s needs the %s role." % (what, label))


def emit(record, event_type, payload):
    """Publish one M46 domain event for `record` (the bridge consumes them)."""
    publish(record.env, event_type, record._name, record.id, payload)


def _vehicle_label(vehicle):
    vehicle = vehicle.sudo()
    return vehicle.name or vehicle.license_plate or ""


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
    "odometer_back": "odometer below the previous fill (or above the next one)",
    "over_capacity": "litres above the tank capacity",
    "duplicate": "duplicate fill (same odometer and litres, or the same receipt)",
    "offroad": "vehicle was off-road on the fill date",
    "odometer_jump": "distance since the previous fill beyond what a full tank covers",
}
# A07 P1 M46-9: the rules a USER's fill is refused for at entry (superuser
# loading is held for review instead); the others hold the fill.
FUEL_REFUSALS = frozenset({"odometer_back", "over_capacity", "duplicate", "offroad"})

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

    # A07 P1 (P2 rule "insert-only records are refused on write/unlink"): a
    # model whose records are evidence (a check, a fill, an off-road record,
    # an accident, a statutory document, a telemetry snapshot) sets this, and
    # no user deletes one; superuser data repair stays possible.
    _fix_insert_only = False

    def _fix_unlink_refusal(self):
        """A reason this record may not be deleted by a user, or None."""
        return "it is part of the fleet record" if self._fix_insert_only else None

    def unlink(self):
        if not self.env.su:
            for rec in self:
                why = rec._fix_unlink_refusal()
                if why:
                    raise UserError(
                        "%s %s cannot be deleted: %s." % (rec._description, rec.display_name, why)
                    )
        return super().unlink()

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
    # A07 P1 M46-6 (BRU-FLT-05): the class was free text that nothing read.
    # It stays free text (live rows hold values such as "professional"), and
    # the BRTA classes it names are parsed into license_class_codes, which the
    # dispatch gate compares with the vehicle's required class.
    license_class = fields.Char(
        string="Licence Class",
        tracking=True,
        help="The BRTA class(es) on the licence: Motorcycle, Light, Medium, Heavy "
        "(e.g. 'Light, Motorcycle').",
    )
    license_class_codes = fields.Char(
        string="Licence Classes (BRTA)",
        compute="_compute_license_class_codes",
        help="The BRTA classes the dispatch gate reads from Licence Class; empty = "
        "not recorded in BRTA terms.",
    )
    license_expiry = fields.Date(string="Licence Expiry", tracking=True)
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
        help="Who suspended the driver. They cannot reinstate the same driver. "
        "Empty on a suspension the system made (an expired licence).",
    )
    # AUT-FLT-04: the smallest alert threshold (days before expiry) already
    # sent for the current licence expiry, so the daily job alerts once each.
    licence_alert_days = fields.Integer(readonly=True, copy=False, default=0)

    _employee_unique = models.Constraint("UNIQUE (employee_id)", "One driver record per employee")

    @api.depends("license_class")
    def _compute_license_class_codes(self):
        labels = dict(LICENCE_CLASSES)
        for rec in self:
            codes = licence_classes(rec.license_class)
            rec.license_class_codes = (
                ", ".join(labels[k] for k, _label in LICENCE_CLASSES if k in codes) or False
            )

    def _fix_licence_classes(self) -> set:
        self.ensure_one()
        return licence_classes(self.license_class)

    def _fix_guarded_fields(self) -> set:
        # A07 P0 recipe M46-6 (D1): any employee reinstated a suspended
        # driver by writing state='active'. The state moves only through
        # action_suspend / action_reinstate, which take a reason.
        return super()._fix_guarded_fields() | {
            "state",
            "suspended_by_id",
            "licence_alert_days",
        }

    @api.model_create_multi
    def create(self, vals_list):
        # A07 P1 M46-6 (AUT-FLT-05) [probe 27]: a driver registered with a
        # licence already expired was born `active`. It is born suspended by
        # the system (no suspender, so any Fleet Officer may reinstate once
        # the renewed licence is recorded).
        recs = super().create(vals_list)
        today = dhaka_today(self)
        for rec in recs.filtered(
            lambda r: r.state == "active" and r.license_expiry and r.license_expiry < today
        ):
            rec._guarded().write({"state": "suspended", "suspended_by_id": False})
            rec.message_post(
                body="Registered suspended: the driving licence expired on %s "
                "(AUT-FLT-05)." % rec.license_expiry
            )
        return recs

    def write(self, vals):
        res = super().write(vals)
        if "license_expiry" in vals:
            # a new expiry date restarts its alert ladder (AUT-FLT-04)
            self.filtered("licence_alert_days")._guarded().write({"licence_alert_days": 0})
        return res

    def action_suspend(self, reason=None):
        # A07 P1 M46-17: suspension is a Fleet Officer decision (any employee
        # could suspend). Superuser code (the licence-expiry job, data repair)
        # is trusted and may state no reason; the trail says it was the system.
        require_role(self.env, FLEET_OFFICER_GROUP, "Suspending a driver")
        if self.env.su and not (isinstance(reason, str) and reason.strip()):
            reason = "system action"
        reason = _reason(reason, "suspending the driver")
        for rec in self:
            if rec.state != "active":
                raise UserError("Suspend an active driver")
            rec._guarded().write(
                {"state": "suspended", "suspended_by_id": False if self.env.su else self.env.uid}
            )
            rec.message_post(
                body="Driver suspended by %s. Reason: %s" % (self.env.user.name, reason)
            )
        return True

    def action_reinstate(self, reason=None):
        """Reinstatement: a second person, a reason, and a licence in date.

        The suspender cannot lift their own suspension (§13 SoD pattern),
        and reinstating a driver whose licence has lapsed or is unrecorded
        would put an unlicensed driver back on the eligible list (BRU-FLT-05)."""
        require_role(self.env, FLEET_OFFICER_GROUP, "Reinstating a driver")
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

    @api.model
    def cron_driver_licence_expiry(self):
        """Daily (data/ir_cron.xml). AUT-FLT-04: licence expiry alerts at the
        configured days (default 60/30/15); AUT-FLT-05: a driver whose licence
        has expired is suspended (removed from assignment eligibility) and the
        bridge is told. Idempotent: an alert is sent once per threshold, a
        suspended driver is not suspended again."""
        Driver = self.sudo()
        today = dhaka_today(self)
        lapsed = Driver.search([("state", "=", "active"), ("license_expiry", "<", today)])
        for rec in lapsed:
            rec.action_suspend(
                reason="the driving licence expired on %s (AUT-FLT-05)" % rec.license_expiry
            )
            emit(
                rec,
                "driver.licence_expired",
                {
                    "driver": rec.name,
                    "driver_id": rec.id,
                    "employee_id": rec.employee_id.id,
                    "licence_class": rec.license_class or "",
                    "expiry_date": str(rec.license_expiry),
                },
            )
        steps = param_days(self.env, LICENCE_ALERT_DAYS_PARAM, LICENCE_ALERT_DAYS_DEFAULT)
        if not steps:
            return True
        for rec in Driver.search(
            [
                ("license_expiry", ">=", today),
                ("license_expiry", "<=", today + timedelta(days=steps[0])),
            ]
        ):
            left = (rec.license_expiry - today).days
            due = [
                d
                for d in steps
                if left <= d and (not rec.licence_alert_days or d < rec.licence_alert_days)
            ]
            if not due:
                continue
            rec._guarded().write({"licence_alert_days": min(due)})
            emit(
                rec,
                "driver.licence_expiring",
                {
                    "driver": rec.name,
                    "driver_id": rec.id,
                    "employee_id": rec.employee_id.id,
                    "licence_class": rec.license_class or "",
                    "expiry_date": str(rec.license_expiry),
                    "days_remaining": left,
                },
            )
        return True


class FixVehicleDocument(models.Model):
    _name = "fix.vehicle.document"
    _description = "Vehicle Statutory Document"
    # A07 P1: the lock mixin (guard + freeze + insert-only). A document with
    # its evidence attached is the record the gate decided on.
    _inherit = ["fix.vehicle.lock.mixin"]
    _order = "valid_to desc, id desc"
    _fix_insert_only = True

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
    # A07 P1 (2026-11-04) M46-20 (D9): `state` was stored and moved to expired
    # only by the nightly job, so for up to a day a lapsed certificate still
    # read "valid". The recorded lifecycle (action_expire, the expiry job) is
    # kept in recorded_state; `state` is that OR the date, decided when read,
    # and searchable, so ("state", "=", "valid") domains keep working.
    recorded_state = fields.Selection(
        [("valid", "Valid"), ("expired", "Expired")],
        string="Recorded State",
        required=True,
        default="valid",
        copy=False,
        help="Expired once recorded so (withdrawn, or processed by the expiry job).",
    )
    state = fields.Selection(
        [("valid", "Valid"), ("expired", "Expired")],
        compute="_compute_state",
        inverse="_inverse_state",
        search="_search_state",
    )
    # A07 P1 M46-5 (FR-FLT-009, AC-21) [probe 23]: a document was valid with
    # no evidence at all. The scan is attached here; without it (and with
    # cd_vehicle_ext.require_document_evidence on, the default) the document
    # proves nothing and the gate does not count it.
    evidence_file = fields.Binary(string="Evidence (scan)", attachment=True, copy=False)
    evidence_filename = fields.Char(string="Evidence File Name", copy=False)
    has_evidence = fields.Boolean(
        compute="_compute_has_evidence", store=True, string="Evidence Attached"
    )
    # Documents recorded before the evidence rule (the live register: 15 rows,
    # none scanned) and superuser data loading. They keep counting while
    # cd_vehicle_ext.legacy_documents_count_valid is on (the deploy-safe
    # default), and are listed as "awaiting evidence" until scanned. A user's
    # new document is never legacy.
    evidence_legacy = fields.Boolean(
        string="Recorded Without Evidence (legacy)",
        readonly=True,
        copy=False,
        help="Recorded before evidence was required, or loaded by data import. "
        "Attach the scan to clear it.",
    )
    evidence_status = fields.Selection(
        [("attached", "Attached"), ("legacy", "Legacy: scan to attach"), ("missing", "Missing")],
        compute="_compute_evidence_status",
        string="Evidence",
    )
    # AUT-FLT-01: the smallest alert threshold already sent for this document.
    alert_days_sent = fields.Integer(readonly=True, copy=False, default=0)
    # A07 audit M46-5 (D9): this was a STORED compute that depends on today's
    # date, recomputed only on write, so with no cron a certificate read
    # "valid" for ever after it ended. Non-stored, it is decided at read time;
    # the search method keeps ("is_valid", "=", True) domains working.
    # Valid = state valid AND valid_from <= today <= valid_to AND evidence
    # (A07 P1): a document with no end date proves nothing about today.
    is_valid = fields.Boolean(compute="_compute_is_valid", search="_search_is_valid")
    # A07 P1 M46-3 [probes 06, 24]: one register, one current document per
    # type. The current one is the LATEST RECORDED document of its type that
    # is in force (valid_from not in the future); recording a newer one
    # supersedes the older, so a lapse or a cancellation recorded after a
    # still-dated certificate is what the gate reads (fail closed). A renewal
    # with a future start does not supersede until it starts.
    is_current = fields.Boolean(compute="_compute_is_current", string="Current")

    @api.depends("recorded_state", "valid_to")
    def _compute_state(self):
        today = dhaka_today(self)
        for rec in self:
            lapsed = bool(rec.valid_to and rec.valid_to < today)
            rec.state = "expired" if rec.recorded_state == "expired" or lapsed else "valid"

    def _inverse_state(self):
        for rec in self:
            rec.recorded_state = rec.state

    def _search_state(self, operator, value):
        if operator in ("=", "in"):
            wanted = {value} if isinstance(value, str) else set(value or ())
        elif operator in ("!=", "not in"):
            wanted = {"valid", "expired"} - (
                {value} if isinstance(value, str) else set(value or ())
            )
        else:
            return NotImplemented
        today = dhaka_today(self)
        valid = [
            ("recorded_state", "=", "valid"),
            "|",
            ("valid_to", "=", False),
            ("valid_to", ">=", today),
        ]
        expired = [
            "|",
            ("recorded_state", "=", "expired"),
            "&",
            ("valid_to", "!=", False),
            ("valid_to", "<", today),
        ]
        if wanted >= {"valid", "expired"}:
            return []
        if wanted == {"valid"}:
            return valid
        if wanted == {"expired"}:
            return expired
        return [("id", "=", 0)]

    @api.depends("evidence_file")
    def _compute_has_evidence(self):
        for rec in self:
            rec.has_evidence = bool(rec.evidence_file)

    @api.depends("has_evidence", "evidence_legacy")
    def _compute_evidence_status(self):
        for rec in self:
            rec.evidence_status = (
                "attached" if rec.has_evidence else ("legacy" if rec.evidence_legacy else "missing")
            )

    def _fix_evidence_ok(self) -> bool:
        self.ensure_one()
        if not param_on(self.env, EVIDENCE_PARAM, default=True):
            return True
        if self.has_evidence:
            return True
        return bool(
            self.evidence_legacy and param_on(self.env, LEGACY_EVIDENCE_PARAM, default=True)
        )

    @api.depends("recorded_state", "valid_from", "valid_to", "has_evidence", "evidence_legacy")
    def _compute_is_valid(self):
        today = dhaka_today(self)
        for rec in self:
            rec.is_valid = rec._fix_covers(today, today)

    def _search_is_valid(self, operator, value):
        if operator != "in":
            return NotImplemented
        today = dhaka_today(self)
        return self._fix_valid_domain(today, today)

    def _compute_is_current(self):
        today = dhaka_today(self)
        current = self._fix_current_map(self.mapped("vehicle_id").ids, today).values()
        ids = {d.id for d in current}
        for rec in self:
            rec.is_current = rec.id in ids

    @api.model
    def _fix_current_map(self, vehicle_ids, day, doc_types=None):
        """{(vehicle id, doc type): document} current on `day` (see is_current)."""
        domain = [
            ("vehicle_id", "in", list(vehicle_ids)),
            "|",
            ("valid_from", "=", False),
            ("valid_from", "<=", day),
        ]
        if doc_types is not None:
            domain.append(("doc_type", "in", list(doc_types)))
        out = {}
        for doc in self.sudo().search(domain, order="id desc"):
            out.setdefault((doc.vehicle_id.id, doc.doc_type), doc)
        return out

    def _fix_covers(self, start, end):
        """True when this document is valid, with its evidence, on every day
        from start to end."""
        self.ensure_one()
        return bool(
            self.state == "valid"
            and self.valid_to
            and self.valid_to >= end
            and (not self.valid_from or self.valid_from <= start)
            and self._fix_evidence_ok()
        )

    @api.model
    def _fix_valid_domain(self, start, end):
        """Domain twin of _fix_covers."""
        domain = [
            ("state", "=", "valid"),
            ("valid_to", ">=", end),
            "|",
            ("valid_from", "=", False),
            ("valid_from", "<=", start),
        ]
        if param_on(self.env, EVIDENCE_PARAM, default=True):
            if param_on(self.env, LEGACY_EVIDENCE_PARAM, default=True):
                domain += ["|", ("has_evidence", "=", True), ("evidence_legacy", "=", True)]
            else:
                domain.append(("has_evidence", "=", True))
        return domain

    def _fix_problem(self, day):
        """Why this (current) document does not cover `day`, or None."""
        self.ensure_one()
        label = dict(self._fields["doc_type"].selection).get(self.doc_type, self.doc_type)
        if self.state != "valid":
            return "%s %s is expired" % (label, self.name)
        if not self.valid_to or self.valid_to < day:
            return "%s %s ended on %s" % (label, self.name, self.valid_to or "(no end date)")
        if not self._fix_evidence_ok():
            return "%s %s has no evidence scan attached" % (label, self.name)
        return None

    def write(self, vals):
        # A07 audit M46-5 (D1): any employee turned an expired fitness
        # certificate valid by writing state='valid' and a new end date, with
        # no evidence. A lapsed document stays lapsed: the renewal is a NEW
        # document with its own number and dates, so the register keeps the
        # history the gate decided on. Superuser code (seeds, data loading,
        # the expiry cron) stays trusted.
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
        res = super().write(vals)
        if "valid_to" in vals:
            # a new end date restarts its alert ladder (AUT-FLT-01)
            self.filtered("alert_days_sent")._guarded().write({"alert_days_sent": 0})
        return res

    def _fix_guarded_fields(self) -> set:
        # A07 P0 recipe M46-5 (D1): `state` was typed by any employee. It is
        # decided at creation from the dates, and afterwards only moves to
        # expired (action_expire, the expiry job); a renewal is a new document.
        return super()._fix_guarded_fields() | {
            "state",
            "recorded_state",
            "evidence_legacy",
            "alert_days_sent",
        }

    def _fix_frozen_fields(self) -> set:
        # A07 P1: once the scan is attached it certifies these facts; a
        # correction is a new document (the old one is superseded).
        if self.has_evidence:
            return {"vehicle_id", "doc_type", "number", "valid_from", "valid_to", "evidence_file"}
        return set()

    @api.model_create_multi
    def create(self, vals_list):
        today = dhaka_today(self)
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.vehicle.document") or "VDOC/New"
                )
            if "state" in vals:
                # the recorded lifecycle is what is stored (M46-20)
                vals.setdefault("recorded_state", vals.pop("state"))
            if self.env.su:
                # data loading: a row with no scan is legacy (counted while the
                # legacy switch is on, and queued for its scan)
                if not vals.get("evidence_file"):
                    vals.setdefault("evidence_legacy", True)
                continue
            # A07 P0 recipe M46-5 (D4): documents were born state=valid, even
            # with no end date. A user's new document is valid only when it
            # has an end date that is not past; recording one as expired (a
            # lapsed certificate, for the history) is always allowed.
            end = fields.Date.to_date(vals.get("valid_to")) or False
            derived = "valid" if end and end >= today else "expired"
            asked = vals.get("recorded_state") or derived
            if asked == "valid" and derived != "valid":
                raise UserError(
                    "A document is recorded as valid only with an end date (Valid To) "
                    "that is not past."
                )
            if vals.get("evidence_legacy") or vals.get("alert_days_sent"):
                self._fix_guard_refuse(["evidence_legacy", "alert_days_sent"])
            vals["recorded_state"] = asked
        if self.env.su:
            return super().create(vals_list)
        # The state was derived above, so it is set through the guard; the
        # records go back in the caller's own environment, without the token.
        return super(FixVehicleDocument, self._guarded()).create(vals_list).with_env(self.env)

    def action_expire(self):
        """Mark a document expired (lapsed, withdrawn or superseded). One-way:
        a renewal is recorded as a new document. A Fleet Officer decision."""
        require_role(self.env, FLEET_OFFICER_GROUP, "Marking a vehicle document expired")
        for rec in self:
            if rec.recorded_state != "valid":
                raise UserError("%s is already expired." % rec.name)
            rec._guarded().write({"recorded_state": "expired"})
        return True

    # ------------------------------------------------------------ scheduler
    @api.model
    def cron_document_expiry(self):
        """Daily at Dhaka midnight (data/ir_cron.xml).

        - FR-FLT-012 / AUT-FLT-02: a document whose end date has passed is
          marked expired, and a vehicle whose CURRENT mandatory document has
          lapsed goes off-road (cause: statutory document) with the event the
          M02/M03 bridge consumes. The dispatch gate already refuses such a
          vehicle; the off-road record makes the stoppage visible and needs a
          renewal with its scan before return (§8.1).
        - FR-FLT-011 / AUT-FLT-01: alerts at the configured days before expiry
          (default 60/30/15/7/1), once per threshold.
        Idempotent; superuser; each effect goes through the guard."""
        Doc = self.sudo()
        today = dhaka_today(self)
        # recorded_state: `state` already reads expired from the date (M46-20);
        # the job records the lapse once and publishes it.
        for doc in Doc.search([("recorded_state", "=", "valid"), ("valid_to", "<", today)]):
            doc._guarded().write({"recorded_state": "expired"})
            emit(
                doc,
                "vehicle.document_expired",
                {
                    "vehicle": _vehicle_label(doc.vehicle_id),
                    "vehicle_id": doc.vehicle_id.id,
                    "document": doc.name,
                    "doc_type": doc.doc_type,
                    "expiry_date": str(doc.valid_to),
                },
            )
        Vehicle = self.env["fleet.vehicle"].sudo()
        vehicles = Vehicle.search([])
        for vid, problems in vehicles._fix_document_problems(
            today, today, lapsed_only=True
        ).items():
            Vehicle.browse(vid)._fix_take_offroad(
                "document", "Statutory document lapsed: %s" % "; ".join(problems)
            )
        steps = param_days(self.env, DOC_ALERT_DAYS_PARAM, DOC_ALERT_DAYS_DEFAULT)
        if steps:
            upcoming = Doc.search(
                [
                    ("state", "=", "valid"),
                    ("valid_to", ">=", today),
                    ("valid_to", "<=", today + timedelta(days=steps[0])),
                ]
            )
            current = {
                d.id
                for d in Doc._fix_current_map(upcoming.mapped("vehicle_id").ids, today).values()
            }
            for doc in upcoming.filtered(lambda d: d.id in current):
                left = (doc.valid_to - today).days
                due = [
                    d
                    for d in steps
                    if left <= d and (not doc.alert_days_sent or d < doc.alert_days_sent)
                ]
                if not due:
                    continue
                doc._guarded().write({"alert_days_sent": min(due)})
                emit(
                    doc,
                    "vehicle.document_expiring",
                    {
                        "vehicle": _vehicle_label(doc.vehicle_id),
                        "vehicle_id": doc.vehicle_id.id,
                        "document": doc.name,
                        "doc_type": doc.doc_type,
                        "expiry_date": str(doc.valid_to),
                        "days_remaining": left,
                    },
                )
        return True

    @api.model
    def _fix_mark_legacy_documents(self):
        """Upgrade hook (data/fix_vehicle_upgrade.xml, every upgrade): a
        document recorded before the evidence rule shipped, with no scan, is
        legacy. Only rows older than the first run are marked, so a user's
        new unscanned document is never made legacy by a later upgrade."""
        ICP = self.env["ir.config_parameter"].sudo()
        since = ICP.get_param("cd_vehicle_ext.evidence_rule_since")
        if not since:
            since = fields.Datetime.to_string(fields.Datetime.now())
            ICP.set_param("cd_vehicle_ext.evidence_rule_since", since)
        self.env.cr.execute(
            """UPDATE fix_vehicle_document
                  SET evidence_legacy = TRUE
                WHERE evidence_legacy IS NOT TRUE
                  AND has_evidence IS NOT TRUE
                  AND create_date <= %s""",
            (since,),
        )
        self.env.invalidate_all()
        return True


class FixVehicleOffroad(models.Model):
    _name = "fix.vehicle.offroad"
    _description = "Vehicle Off-Road Record"
    _inherit = ["fix.vehicle.lock.mixin"]
    _order = "started_on desc, id desc"
    _fix_insert_only = True

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
    # A07 P1 (§8.1): why the vehicle is off the road decides how it returns.
    # A user's report is a defect; the other causes are set by the system
    # (a failed check, an accident, a lapsed document, an overdue service).
    cause = fields.Selection(
        [
            ("defect", "Defect Reported"),
            ("accident", "Accident / Incident"),
            ("document", "Statutory Document Lapsed"),
            ("service", "Service Overdue"),
        ],
        required=True,
        default="defect",
        index=True,
    )
    raised_by_id = fields.Many2one(
        "res.users",
        string="Raised By",
        readonly=True,
        copy=False,
        help="Who took the vehicle off the road (empty = the system). They cannot "
        "return it to service.",
    )
    check_id = fields.Many2one(
        "fix.vehicle.check", string="Failed Check", readonly=True, copy=False, ondelete="set null"
    )
    accident_id = fields.Many2one(
        "fix.vehicle.accident", string="Accident", readonly=True, copy=False, ondelete="set null"
    )
    pm_id = fields.Many2one(
        "fix.vehicle.pm", string="Overdue Service", readonly=True, copy=False, ondelete="set null"
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
        # with no re-check. A07 P1: the cause and its source are the system's.
        return super()._fix_guarded_fields() | {
            "state",
            "ended_on",
            "returned_by_id",
            "return_check_id",
            "cause",
            "raised_by_id",
            "check_id",
            "accident_id",
            "pm_id",
        }

    def _fix_frozen_fields(self) -> set:
        if self.state == "returned":
            return {"vehicle_id", "reason", "started_on"}
        if isinstance(self.id, int):
            # the vehicle an open record stops is not moved to another one
            return {"vehicle_id"}
        return set()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.vehicle.offroad") or "VOFF/New"
                )
        recs = super().create(vals_list)
        if not self.env.su:
            recs._guarded().write({"raised_by_id": self.env.uid})
        for rec in recs:
            # AUT-FLT-02/08/13: M02, M03 and M15 learn the van is off the road
            emit(
                rec,
                "vehicle.off_road",
                {
                    "vehicle": _vehicle_label(rec.vehicle_id),
                    "vehicle_id": rec.vehicle_id.id,
                    "offroad": rec.name,
                    "cause": rec.cause,
                    "reason": rec.reason,
                    "effective_from": str(rec.started_on),
                },
            )
        return recs

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
        """Off-road -> returned to service (§8.1), by a Fleet Officer who did
        not take the vehicle off the road (A07 P0 recipe M46-8; live off-road
        3 was opened and returned by one user the same day).

        - document lapse: the renewal must be in the register, with its scan,
          so every mandatory document is valid today;
        - defect, accident, overdue service: a passed pre-use check recorded
          after the vehicle went off-road (the re-check)."""
        require_role(self.env, FLEET_OFFICER_GROUP, "Returning a vehicle to service")
        today = dhaka_today(self)
        for rec in self:
            if rec.state != "offroad":
                raise UserError("Return an off-road vehicle")
            raiser = rec.raised_by_id or (rec.create_uid if rec.create_uid.id != 1 else False)
            if not self.env.su and raiser and raiser == self.env.user:
                raise UserError(
                    "Segregation of duties: you took %s off the road; another person "
                    "must return it to service." % rec.name
                )
            check = self.env["fix.vehicle.check"]
            if rec.cause == "document":
                problems = rec.vehicle_id._fix_document_problems(today, today).get(
                    rec.vehicle_id.id
                )
                if problems:
                    raise UserError(
                        "%s cannot return to service: %s. Record the renewal with its "
                        "evidence scan first." % (rec.name, "; ".join(problems))
                    )
            else:
                check = rec._fix_return_check()
                if not check:
                    raise UserError(
                        "%s cannot return to service: it needs a passed pre-use check "
                        "recorded after the vehicle went off-road (%s)."
                        % (rec.name, rec.started_on)
                    )
            rec._guarded().write(
                {
                    "state": "returned",
                    "ended_on": fields.Date.context_today(self),
                    "returned_by_id": self.env.uid,
                    "return_check_id": check.id or False,
                }
            )
            emit(
                rec,
                "vehicle.available",
                {
                    "vehicle": _vehicle_label(rec.vehicle_id),
                    "vehicle_id": rec.vehicle_id.id,
                    "offroad": rec.name,
                    "cause": rec.cause,
                    "effective_from": str(rec.ended_on),
                },
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
    _fix_insert_only = True

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
        recs = super().create(vals_list)
        raiser = self.env.user if not self.env.su else None
        for rec in recs:
            failed = [
                label
                for name, label in (
                    ("tyres_ok", "tyres"),
                    ("lights_ok", "lights"),
                    ("fluids_ok", "fluids"),
                    ("brakes_ok", "brakes"),
                )
                if not rec[name]
            ]
            emit(
                rec,
                "vehicle.check_completed",
                {
                    "vehicle": _vehicle_label(rec.vehicle_id),
                    "vehicle_id": rec.vehicle_id.id,
                    "check": rec.name,
                    "driver_id": rec.driver_id.id or False,
                    "checked_on": str(rec.checked_on),
                    "passed": rec.passed,
                    "defects": rec.defects or "",
                },
            )
            if rec.passed:
                continue
            # A07 P1 M46-7 (BRU-FLT-04, AUT-FLT-08) [probe 29]: a failed
            # check left the vehicle on the road. Each of the four items is
            # safety-critical (tyres, lights, fluids, brakes): the vehicle goes
            # off-road now, until a passed re-check by someone else.
            what = rec.defects or "not OK: %s" % ", ".join(failed)
            rec.vehicle_id._fix_take_offroad(
                "defect",
                "Pre-use check %s failed (%s)" % (rec.name, what),
                raised_by=raiser,
                check_id=rec.id,
            )
            emit(
                rec,
                "vehicle.defect_raised",
                {
                    "vehicle": _vehicle_label(rec.vehicle_id),
                    "vehicle_id": rec.vehicle_id.id,
                    "check": rec.name,
                    "defect": what,
                    "safety_critical": True,
                },
            )
        return recs


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
    # A07 P1 M46-13 (BRU-FLT-11, FR-FLT-026) [probe 36]: due on elapsed time
    # OR odometer, whichever first. `is_overdue` is decided at read time.
    due_date = fields.Date(string="Due Date")
    is_overdue = fields.Boolean(
        compute="_compute_is_overdue", search="_search_is_overdue", string="Overdue"
    )
    due_notified = fields.Boolean(readonly=True, copy=False)
    scheduled_on = fields.Date(required=True, default=fields.Date.context_today)
    done_on = fields.Date()
    done_by_id = fields.Many2one("res.users", string="Completed By", readonly=True, copy=False)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    cost = fields.Monetary(currency_field="currency_id")
    state = fields.Selection([("open", "Open"), ("done", "Done")], required=True, default="open")
    notes = fields.Char()

    def _fix_guarded_fields(self) -> set:
        # A07 P0 recipe M46-13 (D1): a plain user wrote state=done with a
        # negative cost and no odometer. Done is set only by action_done.
        return super()._fix_guarded_fields() | {"state", "done_on", "done_by_id", "due_notified"}

    def _fix_frozen_fields(self) -> set:
        # A completed PM is the service history the cost packs read.
        if self.state == "done":
            return {
                "vehicle_id",
                "pm_type",
                "odometer",
                "due_odometer",
                "due_date",
                "scheduled_on",
                "cost",
            }
        return set()

    def _fix_unlink_refusal(self):
        return "a completed service is history" if self.state == "done" else None

    @api.constrains("cost", "odometer", "due_odometer")
    def _check_non_negative(self):
        for rec in self:
            if (rec.cost or 0.0) < 0:
                raise ValidationError("A PM cost cannot be negative.")
            if (rec.odometer or 0) < 0 or (rec.due_odometer or 0) < 0:
                raise ValidationError("An odometer reading cannot be negative.")

    def _fix_overdue(self, tolerance_days=0, tolerance_km=0):
        """True when this open job is past its due date or due odometer by
        more than the tolerance."""
        self.ensure_one()
        if self.state != "open" or not (self.due_date or self.due_odometer):
            return False
        today = dhaka_today(self)
        if self.due_date and self.due_date + timedelta(days=tolerance_days) < today:
            return True
        if self.due_odometer:
            reading = self.vehicle_id.sudo()._fix_last_odometer()
            return reading >= self.due_odometer + tolerance_km
        return False

    def _compute_is_overdue(self):
        for rec in self:
            rec.is_overdue = rec._fix_overdue()

    def _search_is_overdue(self, operator, value):
        if operator != "in":
            return NotImplemented
        candidates = self.search(
            [("state", "=", "open"), "|", ("due_date", "!=", False), ("due_odometer", ">", 0)]
        )
        return [("id", "in", candidates.filtered(lambda r: r._fix_overdue()).ids)]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.vehicle.pm") or "VPM/New"
        return super().create(vals_list)

    def action_done(self):
        """Open -> done, by a Fleet Officer (A07 P1: the creator, any employee,
        completed it). FR-FLT-027: completion records the odometer at service
        and the cost (zero is a valid cost, e.g. a warranty service; negative
        is not)."""
        require_role(self.env, FLEET_OFFICER_GROUP, "Completing a vehicle service")
        for rec in self:
            if rec.state != "open":
                raise UserError("Complete an open PM job")
            if (rec.odometer or 0) <= 0:
                raise UserError(
                    "Record the odometer at service on %s before completing it." % rec.name
                )
            if (rec.cost or 0.0) < 0:
                raise UserError("A PM cost cannot be negative.")
            rec._guarded().write(
                {
                    "state": "done",
                    "done_on": fields.Date.context_today(self),
                    "done_by_id": self.env.uid,
                }
            )
            emit(
                rec,
                "vehicle.service_completed",
                {
                    "vehicle": _vehicle_label(rec.vehicle_id),
                    "vehicle_id": rec.vehicle_id.id,
                    "pm": rec.name,
                    "pm_type": rec.pm_type,
                    "odometer": rec.odometer,
                    "cost": rec.cost,
                    "done_on": str(rec.done_on),
                },
            )
        return True

    @api.model
    def cron_pm_due(self):
        """Daily (data/ir_cron.xml). AUT-FLT-09 / BRU-FLT-11: an open service
        past its due date or due odometer raises `vehicle.service_due` once;
        beyond the tolerance (cd_vehicle_ext.pm_overdue_tolerance_days / _km)
        the vehicle goes off-road when cd_vehicle_ext.pm_overdue_takes_offroad
        is on (off by default: live PM jobs carry no due date yet)."""
        days = int(param_float(self.env, PM_TOLERANCE_DAYS_PARAM, 0))
        km = int(param_float(self.env, PM_TOLERANCE_KM_PARAM, 0))
        offroad = param_on(self.env, PM_OFFROAD_PARAM)
        for rec in self.sudo().search([("is_overdue", "=", True)]):
            if not rec.due_notified:
                rec._guarded().write({"due_notified": True})
                emit(
                    rec,
                    "vehicle.service_due",
                    {
                        "vehicle": _vehicle_label(rec.vehicle_id),
                        "vehicle_id": rec.vehicle_id.id,
                        "pm": rec.name,
                        "trigger": "date"
                        if rec.due_date and rec.due_date < dhaka_today(rec)
                        else "odometer",
                        "due_date": str(rec.due_date or ""),
                        "due_odometer": rec.due_odometer or 0,
                    },
                )
            if offroad and rec._fix_overdue(days, km):
                rec.vehicle_id._fix_take_offroad(
                    "service", "Service %s overdue beyond tolerance" % rec.name, pm_id=rec.id
                )
        return True


class FixVehicleFuel(models.Model):
    _name = "fix.vehicle.fuel"
    _description = "Vehicle Fuel Transaction"
    _inherit = ["fix.vehicle.lock.mixin"]
    _order = "filled_on desc, id desc"
    _fix_insert_only = True

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
    # A07 P1 M46-9 (FR-FLT-034 "duplicate receipts", BRU-FLT-08 evidence):
    # the pump receipt. One receipt number per station is one fill.
    receipt_no = fields.Char(string="Receipt No", copy=False)
    receipt_file = fields.Binary(string="Receipt (scan)", attachment=True, copy=False)
    receipt_filename = fields.Char(string="Receipt File Name", copy=False)
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
        {
            "vehicle_id",
            "driver_id",
            "filled_on",
            "litres",
            "odometer",
            "amount",
            "station",
            "receipt_no",
        }
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
            return set(self._FILL_FIELDS) | {"receipt_file"}
        if isinstance(self.id, int) and self.create_uid and self.create_uid != self.env.user:
            # M46-9 [E 44]: another user raised a recorded amount 4,500 ->
            # 99,999. Only the recorder corrects their own fill, and the
            # correction is re-checked against the rules.
            return {"amount", "litres", "odometer", "receipt_no"}
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
    def _fix_tank_capacity(self, vehicle=None) -> float:
        """The vehicle's own tank capacity when recorded, else the fleet-wide
        ceiling (cd_vehicle_ext.fuel_tank_capacity_litres)."""
        own = vehicle.sudo().fix_tank_capacity_l if vehicle else 0.0
        if own and own > 0:
            return own
        value = param_float(self.env, TANK_CAPACITY_PARAM, TANK_CAPACITY_DEFAULT)
        return value if value > 0 else TANK_CAPACITY_DEFAULT

    def _fix_neighbours(self):
        """(previous, next) accepted fills of the vehicle around this one.
        Accepted = not held and not rejected: a held reading is not yet a
        reading anybody accepted (BRU-FLT-10 "previous accepted reading")."""
        self.ensure_one()
        Fuel = self.sudo().with_context(active_test=False)
        others = [
            ("vehicle_id", "=", self.vehicle_id.id),
            ("id", "!=", self.id),
            ("review_state", "in", ("none", "cleared")),
        ]
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
        following = Fuel.search(
            [
                *others,
                "|",
                ("filled_on", ">", self.filled_on),
                "&",
                ("filled_on", "=", self.filled_on),
                ("id", ">", self.id),
            ],
            order="filled_on asc, id asc",
            limit=1,
        )
        return previous, following

    def _fix_exceptions(self) -> list:
        """The FR-FLT-034 / BRU-FLT-10 rules this fill breaks (keys of
        FUEL_EXCEPTIONS). Reads run as superuser: a rule decides on every fill
        of the vehicle, not only those the recorder can see. A rejected fill
        is not an accepted reading, so it is neither a neighbour nor a
        duplicate."""
        self.ensure_one()
        Fuel = self.sudo().with_context(active_test=False)
        flags = []
        previous, following = self._fix_neighbours()
        if (previous and self.odometer < previous.odometer) or (
            following and self.odometer > following.odometer
        ):
            flags.append("odometer_back")
        if self.litres > self._fix_tank_capacity(self.vehicle_id):
            flags.append("over_capacity")
        twins = Fuel.search(
            [
                ("vehicle_id", "=", self.vehicle_id.id),
                ("id", "!=", self.id),
                ("review_state", "!=", "rejected"),
                ("odometer", "=", self.odometer),
            ]
        )
        same_receipt = False
        if (self.receipt_no or "").strip():
            same_receipt = bool(
                Fuel.search_count(
                    [
                        ("id", "!=", self.id),
                        ("review_state", "!=", "rejected"),
                        ("receipt_no", "=ilike", self.receipt_no.strip()),
                        ("station", "=ilike", (self.station or "").strip()),
                    ]
                )
            )
        if same_receipt or any(abs(f.litres - self.litres) < 0.005 for f in twins):
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
        # A07 P1 (FR-FLT-034 "refuelling intervals inconsistent with distance
        # travelled", BRU-FLT-10 "implausible distance"): more distance since
        # the previous accepted fill than one full tank can cover (tank
        # capacity x the km-per-litre ceiling), so a fill is missing or the
        # odometer is wrong [probe 56: a typo 999,999 after 11,000].
        ceiling = param_float(self.env, FUEL_KM_PER_LITRE_PARAM, FUEL_KM_PER_LITRE_DEFAULT)
        jump = self.odometer - previous.odometer if previous else 0
        if ceiling > 0 and jump > self._fix_tank_capacity(self.vehicle_id) * ceiling:
            flags.append("odometer_jump")
        return flags

    def _fix_apply_exceptions(self):
        """Apply the rules to each fill.

        A07 P1 M46-9 [probes 38/39/40/45]: for a USER the hard rules are a
        refusal at entry (BRU-FLT-10 "rejected for confirmation"): a backwards
        odometer, more litres than the tank holds, the same fill twice (same
        odometer and litres, or the same receipt at the same station), fuel
        for a vehicle that is off the road. An implausible distance is held
        for review (it may be a genuine long trip). Superuser loading (a
        fuel-card feed, a migration) is never refused: every breach holds
        the fill, as in P0. A held fill stays held until reviewed, even if a
        correction clears the breach."""
        for rec in self:
            if rec.review_state in ("cleared", "rejected"):
                continue
            flags = rec._fix_exceptions()
            hard = [f for f in flags if f in FUEL_REFUSALS]
            if hard and not self.env.su:
                raise UserError(
                    "Fuel transaction refused: %s. Check the receipt and the odometer and "
                    "record it again; a genuine exception is loaded through the fuel-card "
                    "import, where it is held for the Logistics Manager's review."
                    % "; ".join(FUEL_EXCEPTIONS[f] for f in hard)
                )
            vals = {"exception_flags": ",".join(flags) or False}
            newly_held = bool(flags and rec.review_state == "none")
            if newly_held:
                vals["review_state"] = "held"
            rec._guarded().write(vals)
            if newly_held:
                emit(
                    rec,
                    "vehicle.fuel_exception",
                    {
                        "vehicle": _vehicle_label(rec.vehicle_id),
                        "vehicle_id": rec.vehicle_id.id,
                        "fuel": rec.name,
                        "driver_id": rec.driver_id.id or False,
                        "rules": flags,
                        "amount": rec.amount,
                    },
                )

    def _fix_emit_recorded(self):
        for rec in self:
            emit(
                rec,
                "vehicle.fuel_recorded",
                {
                    "vehicle": _vehicle_label(rec.vehicle_id),
                    "vehicle_id": rec.vehicle_id.id,
                    "fuel": rec.name,
                    "driver_id": rec.driver_id.id or False,
                    "filled_on": str(rec.filled_on),
                    "litres": rec.litres,
                    "amount": rec.amount,
                    "odometer": rec.odometer,
                    "receipt_no": rec.receipt_no or "",
                },
            )

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
        # BRU-FLT-09: only a fill with no exception reaches M52 now; a held
        # fill reaches it when the reviewer clears it.
        recs.filtered(lambda r: r.review_state == "none")._fix_emit_recorded()
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
        # A07 P1 M46-17 (BRU-FLT-09): the Logistics Manager reviews a held fill.
        require_role(self.env, LOGISTICS_MANAGER_GROUP, "Reviewing a fuel exception")
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
        if decision == "cleared":
            self._fix_emit_recorded()
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
    # A07 P1 M46-14: the state was typed (born `online` with a 30-day-old
    # ping). It is derived from the last ping and moved by the silence job.
    _inherit = ["fix.vehicle.lock.mixin"]
    _order = "last_ping desc, id desc"
    _fix_insert_only = True

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
        default="offline",
    )

    _fuel_range = models.Constraint(
        "CHECK (fuel_level_pct >= 0 AND fuel_level_pct <= 100)",
        "Fuel level is a 0–100 percentage",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state"}

    def _fix_frozen_fields(self) -> set:
        # a snapshot is what the device reported; a newer one is recorded
        if isinstance(self.id, int):
            return {"vehicle_id", "device_ref", "last_ping", "odometer", "fuel_level_pct"}
        return set()

    @api.model
    def _fix_state_for(self, last_ping):
        """online within the silence interval (BRU-FLT-19, FR-FLT-036),
        stale after it, offline when the device never reported."""
        if not last_ping:
            return "offline"
        minutes = param_float(self.env, TELEMATICS_SILENCE_PARAM, TELEMATICS_SILENCE_DEFAULT)
        age = fields.Datetime.now() - fields.Datetime.to_datetime(last_ping)
        return "online" if age <= timedelta(minutes=minutes) else "stale"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.vehicle.telemetry") or "VTEL/New"
                )
        recs = super().create(vals_list)
        for rec in recs:
            state = rec._fix_state_for(rec.last_ping)
            if state != rec.state:
                rec._guarded().write({"state": state})
        return recs

    @api.model
    def cron_telemetry_silence(self):
        """Interval job (data/ir_cron.xml). BRU-FLT-19 / AUT-FLT-12: a snapshot
        that stopped reporting for longer than the configured interval goes
        stale, and for the latest snapshot of each device the bridge is told
        (`vehicle.telematics_silent`: the vehicle is position-unknown to M02).
        Idempotent: only an online snapshot changes."""
        Tel = self.sudo()
        minutes = param_float(self.env, TELEMATICS_SILENCE_PARAM, TELEMATICS_SILENCE_DEFAULT)
        cutoff = fields.Datetime.now() - timedelta(minutes=minutes)
        silent = Tel.search(
            [("state", "=", "online"), "|", ("last_ping", "=", False), ("last_ping", "<", cutoff)]
        )
        latest = {}
        for rec in Tel.search(
            [("vehicle_id", "in", silent.mapped("vehicle_id").ids)], order="last_ping desc, id desc"
        ):
            latest.setdefault((rec.vehicle_id.id, rec.device_ref or ""), rec)
        for rec in silent:
            rec._guarded().write({"state": rec._fix_state_for(rec.last_ping)})
            if latest.get((rec.vehicle_id.id, rec.device_ref or "")) == rec:
                emit(
                    rec,
                    "vehicle.telematics_silent",
                    {
                        "vehicle": _vehicle_label(rec.vehicle_id),
                        "vehicle_id": rec.vehicle_id.id,
                        "device": rec.device_ref or "",
                        "last_report": str(rec.last_ping or ""),
                    },
                )
        return True


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
    _fix_insert_only = True

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
    # A07 P1 M46-10 (P2 "accident claim with evidence and insurer";
    # BRU-FLT-12 photographs and police reference; AUT-FLT-14 injury): the
    # claim names the insurer and carries the evidence before it is closed.
    insurer_id = fields.Many2one(
        "res.partner", string="Insurer", tracking=True, ondelete="restrict"
    )
    police_ref = fields.Char(string="Police Reference (GD/case no.)")
    injury = fields.Boolean(
        string="Injury Involved",
        help="Someone was hurt: the bridge opens the M59 HSE case (AUT-FLT-14).",
    )
    evidence_file = fields.Binary(
        string="Evidence (photos / assessor report)", attachment=True, copy=False
    )
    evidence_filename = fields.Char(string="Evidence File Name", copy=False)
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
                "insurer_id",
                "police_ref",
                "injury",
                "evidence_file",
            }
        if self.state == "claimed":
            # The claim was filed on this vehicle under this reference.
            return {"vehicle_id", "claim_ref"}
        if isinstance(self.id, int):
            return {"vehicle_id"}
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
        recs = super().create(vals_list)
        raiser = self.env.user if not self.env.su else None
        for rec in recs:
            # A07 P1 M46-10 (BRU-FLT-13, AUT-FLT-13) [probe 51]: a reported
            # accident left the vehicle available. It goes off-road until a
            # passed re-check (the roadworthiness assessment) by someone else.
            rec.vehicle_id._fix_take_offroad(
                "accident",
                "Accident %s reported (%s)" % (rec.name, (rec.description or "")[:80]),
                raised_by=raiser,
                accident_id=rec.id,
            )
            emit(
                rec,
                "vehicle.incident",
                {
                    "vehicle": _vehicle_label(rec.vehicle_id),
                    "vehicle_id": rec.vehicle_id.id,
                    "accident": rec.name,
                    "driver_id": rec.driver_id.id or False,
                    "occurred_on": str(rec.occurred_on),
                    "injuries": bool(rec.injury),
                    "damage_cost": rec.damage_cost,
                },
            )
        return recs

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
        insurer's claim reference (given here or already on the record).
        A07 P1: the reporter (who received the insurer's reference) or a
        Fleet Officer files it; nobody else."""
        officer = self.env.su or self.env.user.has_group(FLEET_OFFICER_GROUP)
        for rec in self:
            if rec.state != "reported":
                raise UserError("File a claim for a reported accident")
            if not officer and rec.create_uid != self.env.user:
                raise AccessError(
                    "Filing the claim for %s needs the reporter or a Fleet Officer." % rec.name
                )
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

        The closer is a Logistics Manager (A07 P1), states the settled amount
        (0 for a claim the insurer declined) and is not the person who
        reported the accident. The claim names its insurer and carries its
        evidence (A07 P1). A settlement above Tier 0 must carry a DOFA
        approval of that figure, granted from the approver's inbox.
        Superuser code (data loading) is trusted: with no figure given it
        closes on the recorded settlement."""
        require_role(self.env, LOGISTICS_MANAGER_GROUP, "Closing an insurance claim")
        for rec in self:
            if rec.state != "claimed":
                raise UserError("Close a claimed accident")
            given = settlement
            if self.env.su and (given is None or given is False):
                given = rec.settlement_amount or 0.0
            # 0 is a real answer (a declined claim); only "nothing" is missing
            if given is None or given is False or not str(given).strip():
                raise UserError("State the settled amount to close %s (0 if declined)." % rec.name)
            try:
                amount = float(str(given).replace(",", "").strip())
            except ValueError as exc:
                raise UserError("The settled amount must be a number.") from exc
            if amount < 0:
                raise UserError("The settled amount cannot be negative.")
            if not self.env.su and rec.create_uid == self.env.user:
                raise UserError(
                    "Segregation of duties: you reported %s; another person must close "
                    "its claim." % rec.name
                )
            if not self.env.su:
                missing = [
                    what
                    for what, ok in (
                        ("the insurer", rec.insurer_id),
                        ("the evidence (photos or assessor report)", rec.evidence_file),
                    )
                    if not ok
                ]
                if missing:
                    raise UserError(
                        "Record %s on %s before closing its claim."
                        % (" and ".join(missing), rec.name)
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
