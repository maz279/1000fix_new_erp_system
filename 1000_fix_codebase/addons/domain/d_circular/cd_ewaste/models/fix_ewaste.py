# fix_ewaste - M18: e-waste collection and ESG metrics (P11-M05).
#
# A05 workflow audit (2026-11-03), M18-1/2/5/9/10/16: the collection's state,
# certificate and CO2 fields were writable by any user, so the M06 wipe gate
# inside action_recycle was skipped by a plain write, one verified wipe
# certificate released two items, and the ESG figures were typed. Now:
#  - every workflow, evidence and figure field is guarded (fix.guarded.mixin);
#  - the gate for each target state runs in write() itself, for every caller
#    (an action, a P03 save, JSON-RPC, a superuser service call);
#  - the triage grade routes the item (reuse/refurbish -> M14, hazardous ->
#    the hazmat stream, recycle -> destruction), decided by an assessor;
#  - CO2 avoided is computed from the item's weight and a versioned factor,
#    never typed, and the ESG metrics are computed from the collections.
import logging
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from . import ewaste_common as c

_logger = logging.getLogger(__name__)

EWASTE_STATES = [
    ("collected", "Collected"),
    ("triaged", "Triaged"),
    ("destruction", "Secure Destruction"),
    ("recycled", "Destroyed - Ready for Recycler"),
    ("routed", "Routed to Refurbishment (M14)"),
    ("hazmat", "Hazardous Stream"),
    ("disposed", "Disposed (Hazardous Stream)"),
    ("certified", "Certificate Issued"),
    # M18 capture pass 2 (FR-ESG-023 / BRU-ESG-15): a functional low-value
    # device handed to an approved donation recipient, through the M06 gate
    ("donated", "Donated"),
]

# Where each state may go next (every path: write() checks it).
TRANSITIONS = {
    "collected": {"triaged"},
    "triaged": {"destruction", "routed", "hazmat", "donated"},
    "destruction": {"recycled"},
    "recycled": {"certified"},
    # a revoked recycler certificate returns the item to 'recycled'
    "certified": {"recycled"},
    "hazmat": {"disposed"},
    # A05 S3 M18-13: a unit M14 rejects (harvested for recycling) comes back
    # to its ORIGINAL collection, re-opened for a superseding triage. Only
    # the M14 hand-off consumer (trusted) moves it.
    "routed": {"collected"},
    # A05 S3 M18-07: a revoked certificate returns a disposed hazmat item
    "disposed": {"hazmat"},
    "donated": set(),
}
OPEN_STATES = ("collected", "triaged", "destruction", "recycled", "hazmat")
DIVERTED = ("reuse", "refurbish")
# Grades that leave M18 for M14 (refurbishment, or harvesting into M15 parts,
# FR-ESG-008). Reuse/refurbish route at triage: M14 runs its own wipe gate.
# A harvest is routed by its own step once the M06 gate passes (spec §8.2:
# "Triaged -> harvesting of a storage device: M18 state machine, no bypass").
ROUTED_GRADES = (*DIVERTED, "harvest")

# Changed only through a transition (A05 E3).
_GUARDED = frozenset(
    {
        "state",
        "collected_on",
        "triage_grade",
        "triage_id",
        "data_bearing",
        "wipe_required",
        "batch_id",
        "disposal_certificate_ref",
        "disposal_certificate_id",
        "esg_co2_saved_kg",
        "co2_factor_version",
        "routed_on",
        "storage_extended",
        "storage_overdue",
        "source_model",
        "source_res_id",
        "source_ref",
        "reopened_count",
    }
)
# The item as received: frozen once it leaves triage (M18-5: CO2 derives
# from the weight; M18-2: the device the wipe certificate is bound to).
_FROZEN_AFTER_TRIAGE = frozenset(
    {
        "weight_kg",
        "material_type",
        "item_count",
        "customer_id",
        "event_id",
        "company_id",
    }
)
# The receipt record of FR-ESG-001/003 (capture pass 2): what came in, from
# where, in what condition, with which hazards and photo. The triage decision
# rests on it, so it freezes once the item is triaged, like the device.
_DEVICE_FROZEN = frozenset(
    {
        "device_id",
        "channel",
        "condition",
        "has_battery",
        "has_crt",
        "has_mercury",
        "has_refrigerant",
        "has_toner",
        "photo_attachment_id",
        "collection_point_id",
        "corporate_line_id",
    }
)
_WIPE_FROZEN = frozenset({"wipe_certificate_id"})


class FixEwasteCollection(models.Model):
    """M18: e-waste collection (journey 10: collection -> triage ->
    destruction -> recycling -> disposal certificate)."""

    _name = "fix.ewaste.collection"
    _description = "E-Waste Collection"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, copy=False, readonly=True, default="New")
    customer_id = fields.Many2one("res.partner", string="Customer", required=True, index=True)
    device_id = fields.Many2one("fix.device", string="Device", ondelete="set null")
    event_id = fields.Many2one(
        "fix.ewaste.event", string="Collection Event", ondelete="set null", index=True
    )
    batch_id = fields.Many2one(
        "fix.ewaste.batch", string="Material Batch", ondelete="set null", index=True
    )
    material_type = fields.Selection(
        [
            ("phone", "Mobile Phone"),
            ("laptop", "Laptop"),
            ("tablet", "Tablet"),
            ("accessory", "Accessory"),
            ("battery", "Battery"),
            ("other", "Other"),
        ],
        required=True,
        default="phone",
    )
    weight_kg = fields.Float(
        string="Weight (kg)",
        help="Weighed on receipt. Required: a user records it with the item; an item "
        "handed over by another module is weighed in before triage (M18-14).",
    )
    weight_pending = fields.Boolean(
        string="Awaiting Weigh-in",
        compute="_compute_weight_pending",
        store=True,
        help="Received without a weight (a hand-off): it is weighed in before triage.",
    )
    item_count = fields.Integer(string="Items", default=1)
    collected_on = fields.Date(
        string="Received On", default=c.default_today, index=True, copy=False
    )
    reopened_count = fields.Integer(
        string="Times Re-opened",
        readonly=True,
        copy=False,
        help="Times a unit routed to M14 came back for a superseding triage (M18-13).",
    )
    state = fields.Selection(EWASTE_STATES, default="collected", required=True, tracking=True)
    triage_grade = fields.Selection(
        [
            ("reuse", "Reusable"),
            ("refurbish", "Refurbishable"),
            ("recycle", "Recycle Only"),
            ("hazardous", "Hazardous"),
            ("harvest", "Parts Harvest (M14 / M15)"),
            ("donate", "Donation"),
        ],
        string="Triage Grade",
        help="Set by the assessor's triage decision; it routes the item.",
    )
    triage_id = fields.Many2one(
        "fix.ewaste.triage", string="Triage Decision", readonly=True, copy=False
    )
    data_bearing = fields.Boolean(string="Data Bearing", readonly=True, copy=False)
    wipe_required = fields.Boolean(
        string="M06 Certificate Required",
        default=True,
        readonly=True,
        copy=False,
        help="Fails closed: only an assessor's triage of a non-data item clears it.",
    )
    wipe_certificate_id = fields.Many2one(
        "fix.data.wipe.certificate",
        string="Data Wipe Certificate",
        ondelete="restrict",
        copy=False,
        help="M06's secure wipe; verified and bound to this item before it is released",
    )
    disposal_certificate_ref = fields.Char(
        string="Disposal Certificate Ref",
        readonly=True,
        copy=False,
        help="The recycler disposal certificate that covers this item",
    )
    disposal_certificate_id = fields.Many2one(
        "fix.ewaste.certificate", string="Disposal Certificate", readonly=True, copy=False
    )
    battery_ids = fields.One2many("fix.ewaste.battery", "collection_id", string="Hazmat Records")
    esg_co2_saved_kg = fields.Float(
        string="CO2e Avoided (kg, estimate)",
        readonly=True,
        copy=False,
        help="Computed at recycling: weight x the configured avoided-emissions factor. "
        "An avoided-emissions estimate, reported apart from the inventory.",
    )
    co2_factor_version = fields.Char(string="CO2 Factor Version", readonly=True, copy=False)
    routed_on = fields.Date(readonly=True, copy=False)
    storage_deadline = fields.Date(
        compute="_compute_storage_deadline",
        store=True,
        help="Hazardous Waste (E-waste) Management Rules 2021: 180 days in storage, "
        "plus 90 with a DoE extension.",
    )
    storage_extension_ref = fields.Char(string="DoE Storage Extension Ref", copy=False)
    storage_extended = fields.Boolean(readonly=True, copy=False)
    storage_overdue = fields.Boolean(readonly=True, copy=False, index=True)
    # Where the item came from when another module handed it over (M14
    # harvest -> recycle). A soft link: cd_ewaste does not depend on cd_tradein.
    source_model = fields.Char(string="Source Model", readonly=True, copy=False, index=True)
    source_res_id = fields.Many2oneReference(
        string="Source Record", model_field="source_model", readonly=True, copy=False, index=True
    )
    source_ref = fields.Char(string="Source Reference", readonly=True, copy=False)

    _source_once = models.Constraint(
        "UNIQUE (source_model, source_res_id)",
        "One e-waste collection per handed-over source record",
    )
    _wipe_certificate_once = models.Constraint(
        "UNIQUE (wipe_certificate_id)",
        "One M06 wipe certificate releases one collection item only",
    )
    _weight_positive = models.Constraint(
        "CHECK (weight_kg IS NULL OR weight_kg >= 0)", "Collection weight cannot be negative"
    )

    # ------------------------------------------------------------ guard
    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | _GUARDED

    @api.depends("weight_kg")
    def _compute_weight_pending(self):
        for rec in self:
            rec.weight_pending = (rec.weight_kg or 0.0) <= 0.0

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self:
            if any(r.state != "collected" for r in self):
                locked |= _DEVICE_FROZEN
            if any(r.state not in ("collected", "triaged") for r in self):
                locked |= _FROZEN_AFTER_TRIAGE | _WIPE_FROZEN
            if all(r.storage_extended for r in self):
                locked.add("storage_extension_ref")
        return locked

    def _fix_refuse_frozen(self, vals):
        for rec in self:
            names = {"name"}  # the sequence number never changes
            if rec.state != "collected":
                names |= _DEVICE_FROZEN
            if rec.state not in ("collected", "triaged"):
                names |= _FROZEN_AFTER_TRIAGE | _WIPE_FROZEN
            if rec.storage_extended:
                names.add("storage_extension_ref")
            changed = c.changed_fields(rec, vals, names)
            if changed:
                c.frozen_refuse(rec, changed, "is past triage (%s)" % rec.state)

    @api.depends("collected_on", "storage_extended")
    def _compute_storage_deadline(self):
        days = c.param_int(self.env, c.P_STORAGE_DAYS, c.DEFAULT_STORAGE_DAYS)
        ext = c.param_int(self.env, c.P_STORAGE_EXT_DAYS, c.DEFAULT_STORAGE_EXT_DAYS)
        for rec in self:
            start = rec.collected_on or (rec.create_date and rec.create_date.date())
            rec.storage_deadline = (
                start + timedelta(days=days + (ext if rec.storage_extended else 0))
                if start
                else False
            )

    # ------------------------------------------------------------ rules
    @api.constrains("weight_kg", "material_type", "item_count")
    def _check_weight_plausible(self):
        """M18-5 / F6c: CO2 is derived from the weight, so a weight is bounded
        per item of its material (cd_ewaste.max_item_weight_kg.<material>)."""
        for rec in self:
            if rec.item_count < 1:
                raise ValidationError("A collection holds at least one item.")
            ceiling = c.param_float(
                rec.env,
                c.P_MAX_ITEM_WEIGHT % rec.material_type,
                c.DEFAULT_MAX_ITEM_WEIGHT.get(rec.material_type, 200.0),
            )
            if (rec.weight_kg or 0.0) > ceiling * rec.item_count + 1e-6:
                raise ValidationError(
                    "%s: %.2f kg for %d %s item(s) exceeds the %.2f kg per item ceiling. "
                    "Record the real item count, or weigh it again."
                    % (rec.name, rec.weight_kg, rec.item_count, rec.material_type, ceiling)
                )

    def _fix_serial(self):
        self.ensure_one()
        return self.env["fix.data.wipe.certificate"]._fix_media_serial(self.device_id) or self.name

    def _fix_wipe_denial(self):
        """'' when the item may leave our custody as far as M06 is concerned."""
        self.ensure_one()
        if not self.wipe_required:
            return ""
        cert = self.sudo().wipe_certificate_id
        return cert._fix_certify_denial(self._fix_serial())

    def _check_target_state(self, new_state, vals=None):
        """The gate of each target state. Runs on EVERY path (A05 E4)."""
        self.ensure_one()
        vals = vals or {}
        old = self.state
        if new_state == old:
            return
        if new_state not in TRANSITIONS.get(old, set()):
            raise UserError("%s cannot move from %s to %s." % (self.name, old, new_state))
        grade = vals.get("triage_grade", self.triage_grade)
        if new_state == "triaged" and not grade:
            raise UserError("%s: triage needs the assessor's grade." % self.name)
        if new_state == "triaged" and (vals.get("weight_kg", self.weight_kg) or 0.0) <= 0.0:
            # M18-14: no 0 kg item is assessed (it would vanish from the mass
            # balance and the ESG figures): weigh it in first
            raise UserError(
                "%s has no weight: weigh it in before triage (a hand-off arrives unweighed)."
                % self.name
            )
        if new_state == "destruction" and grade != "recycle":
            raise UserError(
                "%s is graded '%s': only a 'recycle' item goes to secure destruction. "
                "Reuse and refurbish items route to M14; hazardous items go to the "
                "hazmat stream." % (self.name, grade or "untriaged")
            )
        if new_state == "routed" and grade not in ROUTED_GRADES:
            raise UserError(
                "%s: only a reuse, refurbish or harvest item routes to M14." % self.name
            )
        if new_state == "routed" and grade == "harvest":
            # BRU-ESG-01: no storage device is harvested without its certificate
            denial = self._fix_wipe_denial()
            if denial:
                raise UserError(
                    "%s cannot go for parts harvesting: it needs a verified M06 "
                    "certificate bound to it first (%s)." % (self.name, denial)
                )
        if new_state == "donated":
            self._fix_check_donation_gate(grade)
        if new_state == "hazmat" and grade != "hazardous":
            raise UserError("%s: only a hazardous item enters the hazmat stream." % self.name)
        if new_state in ("recycled", "certified"):
            # M18-1 / BRU-ESG-01: the M06 gate on every move out of destruction
            denial = self._fix_wipe_denial()
            if denial:
                raise UserError(
                    "%s cannot be %s: it needs a verified M06 destruction certificate "
                    "bound to it (%s)." % (self.name, new_state, denial)
                )
        if new_state == "certified":
            cert = self.disposal_certificate_id.sudo()
            if not cert or cert.state != "issued" or self not in cert.collection_ids:
                raise UserError(
                    "%s is certified only by an issued recycler disposal certificate "
                    "that lists it (M18-4/10)." % self.name
                )
        if new_state == "disposed":
            hazmat = self.sudo().battery_ids
            open_hazmat = hazmat.filtered(lambda b: b.state != "processed")
            if not hazmat or open_hazmat:
                raise UserError(
                    "%s is disposed only when its hazmat records are processed by the "
                    "recycler." % self.name
                )
            # M18-07: and certified - a hazmat item is in the disposal
            # certificate's scope like any other item
            uncertified = hazmat.filtered(
                lambda b: not b.disposal_certificate_id
                or b.disposal_certificate_id.state != "issued"
            )
            if uncertified:
                raise UserError(
                    "%s is disposed only under an issued recycler disposal certificate that "
                    "covers its hazmat records (%s)."
                    % (self.name, ", ".join(uncertified.mapped("name")))
                )
        if new_state == "collected" and old == "routed" and not self._fix_guard_open():
            raise UserError("%s is re-opened only by M14 sending the unit back." % self.name)

    # ------------------------------------------------------------ ORM
    @api.model_create_multi
    def create(self, vals_list):
        targets = [vals.get("state") or "collected" for vals in vals_list]
        if not self._fix_guard_open() and any(t != "collected" for t in targets):
            self._fix_guard_refuse(["state"])
        if not self._fix_guard_open():
            for vals in vals_list:
                if (vals.get("weight_kg") or 0.0) <= 0.0:
                    # M18-14: an item received at the counter is weighed there
                    raise UserError(
                        "Record the item's weight (kg) on receipt: it drives the mass balance, "
                        "the DoE return and the ESG figures."
                    )
        for vals in vals_list:
            vals.pop("state", None)
            vals["name"] = self.env["ir.sequence"].next_by_code("fix.ewaste.collection") or "EW/New"
        recs = super().create(vals_list)
        for rec, target in zip(recs, targets, strict=True):
            if target != "collected":
                # Trusted code only (a user was refused above). Every item is
                # born 'collected' and walks the transitions, gates included.
                rec._guarded().write({"state": target})
            publish(
                self.env,
                "ewaste.collected",
                "fix.ewaste.collection",
                rec.id,
                {"customer": rec.customer_id.name, "type": rec.material_type},
            )
        return recs

    def write(self, vals):
        if self and not self._fix_guard_open():
            self._fix_refuse_frozen(vals)
        if "state" in vals:
            for rec in self:
                rec._check_target_state(vals["state"], vals)
        if vals.get("wipe_certificate_id"):
            self._fix_check_wipe_attach(vals["wipe_certificate_id"])
        return super().write(vals)

    def _fix_check_wipe_attach(self, cert_id):
        """M18-2: a certificate attached to another item is refused with a
        reason (the UNIQUE constraint is the backstop)."""
        other = self.sudo().search(
            [("wipe_certificate_id", "=", cert_id), ("id", "not in", self.ids)], limit=1
        )
        if other or len(self) > 1:
            raise UserError(
                "Wipe certificate %s already releases %s: one certificate covers one item."
                % (
                    self.env["fix.data.wipe.certificate"].sudo().browse(cert_id).name,
                    other.name or "another item in this selection",
                )
            )

    # ------------------------------------------------------------ actions
    _ASSESSMENT_KEYS = (
        "functional_result",
        "cosmetic_result",
        "market_value_estimate",
        "data_bearing",
        "notes",
        "evidence_file",
        "evidence_filename",
    )

    def action_triage(self, grade, **assessment):
        """The assessor's decision, recorded as a triage record (write-once).

        M18-28: the quick buttons honour the criteria in force - the
        assessment (functional test, photo...) is passed through to the
        decision, and when the criteria need what a button cannot give, the
        refusal says where to record it instead of a bare failure."""
        Triage = self.env["fix.ewaste.triage"]
        extra = {k: v for k, v in assessment.items() if k in self._ASSESSMENT_KEYS and v}
        for rec in self:
            if rec.state != "collected":
                raise UserError("Triage from collected state")
            criteria = self.env["fix.ewaste.triage.criteria"]._fix_in_force(rec.company_id)
            if criteria and not self._fix_guard_open():
                missing = []
                if not extra.get("functional_result"):
                    missing.append("the functional test result")
                if criteria.evidence_required and not extra.get("evidence_file"):
                    missing.append("the assessment photo")
                if missing:
                    raise UserError(
                        "Triage criteria %s are in force: %s needs %s. Record the decision on "
                        "the Triage & Sanitization Record form (FR-ESG-006/007, BRU-ESG-09)."
                        % (criteria.name, rec.name, " and ".join(missing))
                    )
            Triage.create({"collection_id": rec.id, "decision": grade, **extra})

    def _fix_apply_triage(self, triage):
        """Called by the triage record: apply the grade and route the item."""
        self.ensure_one()
        wipe_required = bool(
            triage.wipe_required
            or triage.data_bearing
            or self.device_id
            or self.material_type in c.DATA_MATERIALS
        )
        self._guarded().write(
            {
                "state": "triaged",
                "triage_grade": triage.decision,
                "triage_id": triage.id,
                "data_bearing": bool(triage.data_bearing or self.material_type in c.DATA_MATERIALS),
                "wipe_required": wipe_required,
            }
        )
        publish(
            self.env, "ewaste.triaged", "fix.ewaste.collection", self.id, {"grade": triage.decision}
        )
        if triage.decision in DIVERTED:
            self._fix_route_to_refurbishment()
        elif triage.decision == "hazardous":
            self._fix_open_hazmat()

    def _fix_route_to_refurbishment(self):
        """P2 / G5: a reuse or refurbish item leaves the shredder path and is
        handed to M14 (cd_tradein consumes ewaste.reuse_routed)."""
        for rec in self:
            rec._guarded().write({"state": "routed", "routed_on": c.today(rec.env)})
            publish(
                rec.env,
                "ewaste.reuse_routed",
                "fix.ewaste.collection",
                rec.id,
                {
                    "collection": rec.name,
                    "grade": rec.triage_grade,
                    "device_id": rec.device_id.id or None,
                    "serial": rec._fix_serial(),
                    "customer_id": rec.customer_id.id,
                    "material_type": rec.material_type,
                    "weight_kg": rec.weight_kg,
                    "data_bearing": rec.data_bearing,
                    "wipe_certificate_id": rec.wipe_certificate_id.id or None,
                    "company_id": rec.company_id.id,
                },
            )

    def _fix_open_hazmat(self):
        """M18-8 / B4: a hazardous item opens its hazmat record and leaves the
        data-destruction (shredder) path."""
        Battery = self.env["fix.ewaste.battery"].sudo()
        for rec in self:
            if not rec.battery_ids:
                Battery.create(
                    {
                        "collection_id": rec.id,
                        "company_id": rec.company_id.id,
                        "operating_unit_id": rec.operating_unit_id.id or False,
                        "chemistry": "li_ion" if rec.material_type == "battery" else "other",
                        "weight_kg": rec.weight_kg or 0.0,
                    }
                )
            rec._guarded().write({"state": "hazmat"})

    def _fix_require_operator(self, doing):
        """M18-28: destruction and release are the e-waste floor's (a
        dispatcher or an assessor), not any user's."""
        if not (
            self.env.su
            or self.env.user.has_group(c.G_DISPATCH)
            or self.env.user.has_group(c.G_ASSESSOR)
        ):
            raise UserError("Only an E-Waste Dispatcher or Triage Assessor may %s." % doing)

    def action_secure_destruction(self):
        """Secure destruction through M06 — the wipe certificate must
        exist before destruction begins (journey 10's gate)."""
        self._fix_require_operator("start secure destruction")
        for rec in self:
            if rec.state != "triaged":
                raise UserError("Destruction from triaged state")
            if not rec.wipe_certificate_id:
                Wipe = self.env["fix.data.wipe.certificate"]
                wipe = Wipe.create(
                    {
                        "device_id": rec.device_id.id,
                        "method": "physical_destruction",
                        # A02 audit M06-1: bound to the one item it certifies
                        "serial_number": Wipe._fix_media_serial(rec.device_id) or rec.name,
                    }
                )
                rec.write({"wipe_certificate_id": wipe.id})
            rec._guarded().write({"state": "destruction"})
            publish(self.env, "ewaste.destruction_started", "fix.ewaste.collection", rec.id, {})

    def _fix_co2_avoided(self):
        self.ensure_one()
        factor, version = c.co2_factor(self.env, self.company_id)
        return round((self.weight_kg or 0.0) * factor, 3), version

    def action_recycle(self, co2_saved=None):
        """Release the destroyed item for the recycler. The M06 gate runs in
        write() (every path). CO2 avoided is computed, never typed (M18-5)."""
        self._fix_require_operator("release an item for the recycler")
        for rec in self:
            if rec.state != "destruction":
                raise UserError("Recycle from destruction state")
            co2, version = rec._fix_co2_avoided()
            if co2_saved is not None and abs(float(co2_saved) - co2) > 0.001:
                raise UserError(
                    "CO2 avoided is computed from the weight (%.3f kg CO2e, factor %s); "
                    "it cannot be typed (BRU-ESG-11)." % (co2, version)
                )
            denial = rec._fix_wipe_denial()
            if denial:
                raise UserError(
                    "Recycle needs a verified M06 destruction certificate (%s)" % denial
                )
            rec._guarded().write(
                {"state": "recycled", "esg_co2_saved_kg": co2, "co2_factor_version": version}
            )

    def action_issue_certificate(self):
        """Journey 10's ending: certify the item from the recycler disposal
        certificate of its processed batch (M18-4/10). There is no string
        certificate any more."""
        for rec in self:
            if rec.state != "recycled":
                raise UserError("Certificate from recycled state")
            batch = rec.batch_id
            if not batch or batch.state != "processed":
                raise UserError(
                    "%s has no processed recycler batch: a disposal certificate comes from "
                    "the recycler that processed it." % rec.name
                )
            cert = batch.certificate_ids.filtered(lambda x: x.state in ("draft", "issued"))[:1]
            if not cert:
                raise UserError(
                    "Batch %s has no recycler disposal certificate recorded yet." % batch.name
                )
            if cert.state == "draft":
                cert.action_issue()
            elif rec not in cert.collection_ids:
                raise UserError("Certificate %s does not list %s." % (cert.name, rec.name))

    def action_triage_reuse(self, **assessment):
        self.action_triage("reuse", **assessment)

    def action_triage_refurbish(self, **assessment):
        self.action_triage("refurbish", **assessment)

    def action_triage_recycle(self, **assessment):
        self.action_triage("recycle", **assessment)

    def action_triage_hazardous(self, **assessment):
        self.action_triage("hazardous", **assessment)

    def action_recycle_estimated(self):
        """Recycle with the CO2 avoided computed from the configured factor."""
        self.action_recycle()

    def action_remove_from_batch(self):
        """Take a ready item out of a batch that has not left yet."""
        c.require_group(self.env, c.G_DISPATCH, "E-Waste Dispatcher", "change a batch")
        for rec in self:
            if not rec.batch_id or rec.batch_id.state != "draft":
                raise UserError("%s is not in a draft batch." % rec.name)
            rec._guarded().write({"batch_id": False})

    def action_apply_storage_extension(self):
        """Record the DoE's 90-day storage extension (Rules 2021)."""
        c.require_group(
            self.env, c.G_COMPLIANCE, "E-Waste Compliance Officer", "record a storage extension"
        )
        for rec in self:
            if rec.storage_extended:
                raise UserError("%s already has its one storage extension." % rec.name)
            if not (rec.storage_extension_ref or "").strip():
                raise UserError("Enter the DoE extension permission reference first.")
            rec._guarded().write({"storage_extended": True, "storage_overdue": False})
            rec.message_post(
                body="DoE storage extension %s recorded by %s."
                % (rec.storage_extension_ref, rec.env.user.name)
            )

    # ------------------------------------------------------------ consumers
    _DEVICE_MATERIAL = {"smartphone": "phone", "tablet": "tablet", "laptop": "laptop"}

    @api.model
    def consume_tradein_harvested(self, event):
        """tradein.harvested (M14) -> the harvested unit enters M18 when its
        target is 'recycle'. Superuser-only (the event relay) and idempotent:
        one collection per trade-in, a repeat is a no-op. Everything is
        re-read from the harvest record; the payload is not trusted. The
        unit then goes through M18's own triage, wipe and dispatch gates."""
        if not self.env.su:
            raise UserError("consume_tradein_harvested runs only from the event relay.")
        if "fix.tradein.harvest" not in self.env or event.get("aggregate") not in (
            None,
            "fix.tradein.harvest",
        ):
            return self.browse()
        harvest = self.env["fix.tradein.harvest"].sudo().browse(event.get("aggregate_id") or 0)
        harvest = harvest.exists()
        if not harvest or harvest.state != "harvested" or harvest.target != "recycle":
            return self.browse()
        tradein = harvest.tradein_id
        if not tradein:
            return self.browse()
        existing = self.sudo().search(
            [("source_model", "=", tradein._name), ("source_res_id", "=", tradein.id)], limit=1
        )
        if existing:
            return existing
        original = self._fix_original_of(tradein)
        if original:
            # M18-13: the unit came from M18 in the first place - it returns
            # to its own collection (weight, customer, intake history intact)
            # for a superseding triage, never as a new 0 kg item
            return original._fix_reopen_from_m14(tradein, harvest)
        device = tradein.device_id
        cert = tradein.wipe_certificate_id
        if cert and self.sudo().search_count([("wipe_certificate_id", "=", cert.id)]):
            cert = cert.browse()  # one certificate releases one item; M18 re-checks
        col = (
            self.sudo()
            ._guarded()
            .create(
                {
                    "company_id": tradein.company_id.id,
                    "operating_unit_id": tradein.operating_unit_id.id or False,
                    # the unit is the company's own stock once it was bought in
                    "customer_id": tradein.company_id.partner_id.id,
                    "device_id": device.id or False,
                    "material_type": self._DEVICE_MATERIAL.get(device.device_type, "other")
                    if device
                    else "other",
                    "wipe_certificate_id": cert.id or False,
                    "source_model": tradein._name,
                    "source_res_id": tradein.id,
                    "source_ref": tradein.name,
                }
            )
        )
        col.message_post(
            body="Received from M14 trade-in %s: harvest %s (%s) targeted recycling."
            % (tradein.name, harvest.name, harvest.component)
        )
        # never hand back a record that still carries the guard token
        return self.browse(col.id)

    @api.model
    def _fix_original_of(self, tradein):
        """The e-waste collection a trade-in intake was opened from (M14
        records it as ewaste_collection_id when it consumes reuse routing)."""
        coll_id = tradein.ewaste_collection_id if "ewaste_collection_id" in tradein._fields else 0
        if not coll_id:
            return self.browse()
        return self.sudo().browse(int(coll_id)).exists()

    def _fix_reopen_from_m14(self, tradein, harvest=None):
        """Re-open this routed collection for a superseding triage: back to
        'collected', the earlier grade cleared (its triage record stays, write-
        once, as history). Trusted path (the M14 hand-off relay)."""
        self.ensure_one()
        if self.state != "routed" and self.reopened_count:
            return self.browse(self.id)  # a repeat delivery: already re-opened
        if self.state != "routed":
            raise UserError(
                "%s is %s, not routed to M14: M14 cannot send it back." % (self.name, self.state)
            )
        previous = self.triage_id
        self.sudo()._guarded().write({"state": "collected"})
        self.sudo()._guarded().write(
            {
                "triage_grade": False,
                "triage_id": False,
                "reopened_count": self.reopened_count + 1,
                "channel": "refurb_failed",
            }
        )
        self.sudo().message_post(
            body="Returned by M14 trade-in %s%s: re-opened for a new triage that supersedes %s."
            % (
                tradein.name,
                " (harvest %s, %s)" % (harvest.name, harvest.component) if harvest else "",
                previous.name or "the earlier decision",
            )
        )
        return self.browse(self.id)

    @api.model
    def consume_stock_written_off(self, event):
        """stock.written_off (M15, spec §12: consumers M19, M18) -> the scrapped
        quantity enters M18 for disposal. Superuser-only (the event relay) and
        idempotent: one collection per write-off. Everything is re-read from the
        quarantine record; the payload is not trusted. No value crosses over."""
        if not self.env.su:
            raise UserError("consume_stock_written_off runs only from the event relay.")
        if "fix.stock.quarantine" not in self.env or event.get("aggregate") not in (
            None,
            "fix.stock.quarantine",
        ):
            return self.browse()
        scrap = self.env["fix.stock.quarantine"].sudo().browse(event.get("aggregate_id") or 0)
        scrap = scrap.exists()
        if not scrap or scrap.state != "scrapped":
            return self.browse()
        existing = self.sudo().search(
            [("source_model", "=", scrap._name), ("source_res_id", "=", scrap.id)], limit=1
        )
        if existing:
            return existing
        part = scrap.part_id
        col = (
            self.sudo()
            ._guarded()
            .create(
                {
                    "company_id": scrap.company_id.id,
                    "operating_unit_id": scrap.location_id.operating_unit_id.id or False,
                    # written-off stock is the company's own
                    "customer_id": scrap.company_id.partner_id.id,
                    "material_type": "battery" if part.part_category == "battery" else "other",
                    "item_count": int(round(scrap.qty or 0.0)),
                    "source_model": scrap._name,
                    "source_res_id": scrap.id,
                    "source_ref": scrap.name,
                }
            )
        )
        col.message_post(
            body="Received from M15 write-off %s: %s x %s."
            % (scrap.name, scrap.qty, part.part_number)
        )
        # never hand back a record that still carries the guard token
        return self.browse(col.id)

    # ------------------------------------------------------------ cron
    @api.model
    def cron_storage_clock(self):
        """E12: the 180-day (+90) storage clock. Flags items still in our
        custody past their deadline and warns ahead of it. Safe to re-run."""
        today = c.today(self.env)
        warn_days = c.param_int(self.env, c.P_RETURN_REMINDER_DAYS, c.DEFAULT_REMINDER_DAYS)
        held = self.sudo().search(
            [
                ("state", "in", OPEN_STATES),
                ("storage_deadline", "!=", False),
                "|",
                ("batch_id", "=", False),
                ("batch_id.state", "=", "draft"),
            ]
        )
        # M18-27: a hazmat item whose cells have all left storage (batched and
        # dispatched) is no longer held, whatever its own state says
        held = held.filtered(
            lambda r: r.state != "hazmat"
            or not r.battery_ids
            or any(b.state == "stored" for b in r.battery_ids)
        )
        overdue = held.filtered(lambda r: r.storage_deadline < today)
        for rec in overdue.filtered(lambda r: not r.storage_overdue):
            rec._guarded().write({"storage_overdue": True})
            c.notify(
                rec,
                "E-waste storage limit passed",
                "%s has been in storage past %s (Rules 2021: 180 days, +90 with a DoE "
                "extension). Dispatch it to a licensed recycler or record the extension."
                % (rec.name, rec.storage_deadline),
                c.G_COMPLIANCE,
            )
        for rec in held - overdue:
            if rec.storage_deadline <= today + timedelta(days=warn_days):
                c.notify(
                    rec,
                    "E-waste storage limit approaching",
                    "%s must leave storage by %s." % (rec.name, rec.storage_deadline),
                    c.G_COMPLIANCE,
                )
        cleared = self.sudo().search([("storage_overdue", "=", True)]) - overdue
        if cleared:
            cleared._guarded().write({"storage_overdue": False})
        return len(overdue)


class FixEsgMetric(models.Model):
    """M18: ESG metrics feeding M25's reporting (BM-004).

    A05 audit M18-5 / BRU-ESG-11: a metric is COMPUTED from the collections of
    its company and period, never typed. Users read; the compute runs as
    trusted code. Avoided CO2 carries scope 'avoided' and the factor version,
    and is never added to the inventory figures."""

    _name = "fix.esg.metric"
    _description = "ESG Metric"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "period desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    metric_type = fields.Selection(
        [
            ("co2_saved", "CO2e Avoided (kg, estimate)"),
            ("ewaste_collected", "E-Waste Collected (kg)"),
            ("devices_refurbished", "Devices Diverted to Reuse/Refurbishment"),
            ("energy_saved", "Energy Saved (kWh)"),
        ],
        required=True,
        default="co2_saved",
    )
    period = fields.Char(required=True, help="YYYY-MM")
    value = fields.Float(required=True)
    # stored compute (not an onchange-only value): metrics created by the API,
    # a seed or an import must carry their unit too, not just the web form
    unit = fields.Char(compute="_compute_unit", store=True, readonly=True)
    scope = fields.Selection(
        [("inventory", "Inventory (measured)"), ("avoided", "Avoided (estimate)")],
        compute="_compute_scope",
        store=True,
    )
    computed = fields.Boolean(
        readonly=True,
        help="Computed from the collections. Rows without it were typed before the "
        "A05 audit and are excluded from every report.",
    )
    factor_version = fields.Char(readonly=True)
    source_count = fields.Integer(string="Source Records", readonly=True)
    computed_at = fields.Datetime(readonly=True)

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | {
            "value",
            "metric_type",
            "period",
            "company_id",
            "computed",
            "factor_version",
            "source_count",
            "computed_at",
        }

    @api.model_create_multi
    def create(self, vals_list):
        # BRU-ESG-11: no entry path. Only the compute (token) or trusted code.
        if not self._fix_guard_open():
            raise UserError(
                "ESG metrics are computed from the e-waste collections and cannot be "
                "entered (BRU-ESG-11). Use Recompute."
            )
        return super().create(vals_list)

    @api.depends("metric_type")
    def _compute_unit(self):
        units = {
            "co2_saved": "kg",
            "ewaste_collected": "kg",
            "devices_refurbished": "count",
            "energy_saved": "kWh",
        }
        for rec in self:
            rec.unit = units.get(rec.metric_type, "")

    @api.depends("metric_type")
    def _compute_scope(self):
        for rec in self:
            rec.scope = "avoided" if rec.metric_type == "co2_saved" else "inventory"

    # ------------------------------------------------------------ compute
    @api.model
    def _fix_figures(self, company, period):
        """{metric_type: (value, source count, factor version)} for one period."""
        bounds = c.period_bounds(period)
        if not bounds:
            raise UserError("Period %r is not YYYY, YYYY-MM or YYYY-Qn." % period)
        start, end = bounds
        Col = self.env["fix.ewaste.collection"].sudo()
        base = [("company_id", "=", company.id)]
        received = Col.search([*base, ("collected_on", ">=", start), ("collected_on", "<=", end)])
        certified = Col.search(
            [
                *base,
                ("state", "=", "certified"),
                ("disposal_certificate_id.issued_on", ">=", start),
                ("disposal_certificate_id.issued_on", "<=", end),
            ]
        )
        diverted = Col.search(
            [*base, ("state", "=", "routed"), ("routed_on", ">=", start), ("routed_on", "<=", end)]
        )
        versions = sorted(set(certified.mapped("co2_factor_version")) - {False})
        return {
            "ewaste_collected": (
                round(sum(received.mapped("weight_kg")), 3),
                len(received),
                False,
            ),
            "co2_saved": (
                round(sum(certified.mapped("esg_co2_saved_kg")), 3),
                len(certified),
                ", ".join(versions) or c.co2_factor(self.env, company)[1],
            ),
            "devices_refurbished": (
                float(sum(diverted.mapped("item_count"))),
                len(diverted),
                False,
            ),
        }

    @api.model
    def compute_period(self, period, company=None):
        """Create or refresh the computed metrics of one company and period.
        Idempotent; runs as trusted code."""
        company = company or self.env.company
        Metric = self.sudo()
        labels = dict(self._fields["metric_type"].selection)
        out = Metric.browse()
        for mtype, (value, count, version) in self._fix_figures(company, period).items():
            row = Metric.search(
                [
                    ("company_id", "=", company.id),
                    ("period", "=", period),
                    ("metric_type", "=", mtype),
                    ("computed", "=", True),
                ],
                limit=1,
            )
            vals = {
                "value": value,
                "source_count": count,
                "factor_version": version,
                "computed_at": fields.Datetime.now(),
            }
            if row:
                row._guarded().write(vals)
            else:
                row = Metric._guarded().create(
                    {
                        **vals,
                        "name": "%s %s" % (labels[mtype], period),
                        "company_id": company.id,
                        "period": period,
                        "metric_type": mtype,
                        "computed": True,
                    }
                )
            out |= row
        # the rows were written under the guard token: return them without it
        return self.browse(out.ids)

    def action_recompute(self):
        """Recompute the periods of these metrics from the collections."""
        done = set()
        for rec in self:
            key = (rec.company_id.id, rec.period)
            if key in done or rec.company_id not in self.env.companies:
                continue
            done.add(key)
            self.compute_period(rec.period, rec.company_id)
        return True

    @api.model
    def cron_recompute(self):
        """Refresh this month and last month for every company."""
        today = c.today(self.env)
        last = today.replace(day=1) - timedelta(days=1)
        for company in self.env["res.company"].sudo().search([]):
            for period in {today.strftime("%Y-%m"), last.strftime("%Y-%m")}:
                self.compute_period(period, company)
        return True

    def _fix_consume_month(self, event, field_date):
        rec = self.env["fix.ewaste.collection"].sudo().browse(event.get("aggregate_id")).exists()
        if not rec:
            return
        day = field_date(rec)
        if day:
            self.compute_period(day.strftime("%Y-%m"), rec.company_id)

    @api.model
    def consume_collection_recorded(self, event):
        """ewaste.collected -> refresh the inventory of its month."""
        self._fix_consume_month(event, lambda r: r.collected_on)

    @api.model
    def consume_certificate_issued(self, event):
        """ewaste.certificate_issued -> refresh the avoided CO2 of its month."""
        self._fix_consume_month(event, lambda r: r.disposal_certificate_id.issued_on)

    @api.model
    def consume_reuse_routed(self, event):
        """ewaste.reuse_routed -> refresh the devices diverted of its month."""
        self._fix_consume_month(event, lambda r: r.routed_on)
