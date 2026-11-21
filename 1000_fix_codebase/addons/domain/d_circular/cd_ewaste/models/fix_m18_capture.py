# fix_m18_capture - M18 capture pass 2 (19 Nov 2026).
#
# The 13 Nov capture audit gave every M18 sub-module page a button, and listed
# what the specification names as captured on those pages but had no model at
# all. Read against FR-ESG-001..026, the BRU-ESG rules and the owned entities
# of spec §10.1, these records are built here (imported last):
#
#   p1  the receipt record (FR-ESG-001/003): channel, condition, hazard flags,
#       photo, collection point; the corporate disposal contract reconciled
#       to the client's declared assets (FR-ESG-005, BRU-ESG-14, AC-15)
#   p2  the published triage criteria the assessor applies (FR-ESG-006/007,
#       BRU-ESG-09); the harvest route (FR-ESG-008) and the donation route
#       through the M06 gate (FR-ESG-023, BRU-ESG-15)
#   p4  the recycler's declared downstream vendors, verified annually and
#       checked at dispatch (FR-ESG-024, BRU-ESG-18)
#   p5  the item NOT on the recycler's certificate, as an exception
#       (FR-ESG-013, BRU-ESG-04, AC-07); material recovery by class, weight
#       and agreed rate, raised as batch income (FR-ESG-014, BRU-ESG-19)
#   p6/7 the collection point register with per-class hazmat ceilings
#       (FR-ESG-022, T-06, BRU-ESG-07)
#   p9  the versioned, approved emissions factor set (FR-ESG-019, T-08)
#   p10 the regulatory obligation register, reviewed at least quarterly
#       (FR-ESG-016, BRU-ESG-16, AUT-ESG-19)
#
# Every decision is a method that checks its role; where the spec separates
# duties, the person who recorded a thing does not approve it.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from . import ewaste_common as c
from .fix_ewaste import OPEN_STATES
from .fix_ewaste_ops import MATERIALS, _seq

# Storage ceiling classes (T-06): lithium cells are split by condition because
# damaged / swollen cells follow the stricter path (BRU-ESG-08).
HAZ_CLASSES = [
    ("li_sound", "Lithium Cells - Sound"),
    ("li_damaged", "Lithium Cells - Damaged / Swollen"),
    ("lead_acid", "Lead-Acid Batteries"),
    ("other_battery", "Other Batteries (NiMH and other)"),
    ("crt", "CRT Glass (lead)"),
    ("mercury_lamp", "Mercury-Containing Lamps"),
    ("refrigerant", "Refrigerant-Bearing Equipment"),
    ("toner", "Toner / Ink Cartridges"),
]

# FR-ESG-014: the recovered material classes the spec names.
RECOVERY_CLASSES = [
    ("ferrous", "Ferrous Metal"),
    ("non_ferrous", "Non-Ferrous Metal"),
    ("precious", "Precious Metals"),
    ("pcb", "Circuit Boards"),
    ("plastic", "Plastics"),
    ("glass", "Glass"),
    ("cabling", "Cabling"),
    ("battery_mass", "Battery Black Mass"),
    ("other", "Other"),
]

# P_DOWNSTREAM_DAYS: how old a downstream verification may be at dispatch.
P_DOWNSTREAM_DAYS = "cd_ewaste.downstream_verification_days"
DEFAULT_DOWNSTREAM_DAYS = 365
# BRU-ESG-16: the regulatory register is reviewed at least quarterly.
MAX_REVIEW_DAYS = 92
REVIEW_DAYS = {"monthly": 31, "quarterly": 92, "annual": 365, "event": 92}

# The items a corporate disposal can be closed on (BRU-ESG-14).
_RECONCILED = ("certified", "disposed", "donated")


def _hazard_class(chemistry, swollen):
    if chemistry in ("li_ion", "li_po"):
        return "li_damaged" if swollen else "li_sound"
    if chemistry == "lead_acid":
        return "lead_acid"
    if chemistry in ("nimh", "other"):
        return "other_battery"
    return chemistry


def _upload_once(rec, data, name, link):
    """Attach a staged file to its record and fill the link (trusted)."""
    if not data:
        return
    att = rec.env["ir.attachment"].create(
        {
            "name": (name or "").strip()
            or "%s - %s" % (rec.display_name, rec._fields[link].string),
            "datas": data,
            "res_model": rec._name,
            "res_id": rec.id,
        }
    )
    rec.sudo()._guarded().write({link: att.id})


# ============================================================ p6/p7 points
class FixEwasteCollectionPoint(models.Model):
    """A designated collection point (FR-ESG-022): its capacity, storage
    constraints, hazardous-material ceilings by class and responsible person.
    Registered by anyone; activated by an HSE officer who did not register it;
    its ceilings are frozen while it is active (reopen to change them)."""

    _name = "fix.ewaste.collection.point"
    _description = "E-Waste Collection Point"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Branch / Unit")
    kind = fields.Selection(
        [
            ("branch", "Branch Drop-off Counter"),
            ("public_bin", "Public Collection Bin"),
            ("warehouse", "Warehouse Holding Area"),
            ("hazmat_store", "Hazardous Material Store"),
        ],
        required=True,
        default="branch",
    )
    address = fields.Char()
    responsible_id = fields.Many2one("hr.employee", string="Responsible Person")
    capacity_kg = fields.Float(string="Capacity (kg)")
    storage_constraints = fields.Text(
        help="Segregation, ventilation, temperature and suppression the location provides."
    )
    limit_ids = fields.One2many(
        "fix.ewaste.collection.point.limit", "point_id", string="Hazardous Ceilings"
    )
    active_from = fields.Date(default=fields.Date.context_today)
    active_to = fields.Date()
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("closed", "Closed")],
        required=True,
        default="draft",
    )
    approved_by_id = fields.Many2one("res.users", string="Activated By", readonly=True)
    approved_on = fields.Date(string="Activated On", readonly=True)
    held_kg = fields.Float(string="Held Now (kg)", compute="_compute_held")
    notes = fields.Text()

    _dates_ordered = models.Constraint(
        "CHECK (active_to IS NULL OR active_from IS NULL OR active_to >= active_from)",
        "A collection point cannot close before it opens",
    )
    _capacity_positive = models.Constraint(
        "CHECK (capacity_kg IS NULL OR capacity_kg >= 0)", "Capacity cannot be negative"
    )

    _TERMS = frozenset(
        {"kind", "capacity_kg", "company_id", "responsible_id", "storage_constraints", "name"}
    )

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | {"state", "approved_by_id", "approved_on"}

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(r.state != "draft" for r in self):
            locked |= self._TERMS | {"limit_ids"}
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                if rec.state != "draft":
                    changed = c.changed_fields(rec, vals, self._TERMS)
                    if changed or "limit_ids" in vals:
                        c.frozen_refuse(
                            rec,
                            changed or {"limit_ids"},
                            "is %s (an HSE officer reopens it to change it)" % rec.state,
                        )
        return super().write(vals)

    def _compute_held(self):
        Col = self.env["fix.ewaste.collection"].sudo()
        for rec in self:
            if not rec.id:
                rec.held_kg = 0.0
                continue
            held = Col.search([("collection_point_id", "=", rec.id), ("state", "in", OPEN_STATES)])
            rec.held_kg = round(sum(held.mapped("weight_kg")), 3)

    def _fix_limit_for(self, hazard_class):
        self.ensure_one()
        return self.limit_ids.filtered(lambda x: x.hazard_class == hazard_class)[:1]

    def action_activate(self):
        c.require_group(self.env, c.G_HSE, "E-Waste HSE Officer", "activate a collection point")
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is not a draft." % rec.name)
            if not self.env.su and rec.create_uid == self.env.user:
                raise UserError("You registered %s: another HSE officer activates it." % rec.name)
            if not rec.responsible_id or rec.capacity_kg <= 0:
                raise UserError(
                    "%s needs its responsible person and its capacity first." % rec.name
                )
            if rec.kind == "hazmat_store" and not rec.limit_ids:
                raise UserError(
                    "%s is a hazardous material store: set a ceiling for each class it "
                    "may hold (T-06)." % rec.name
                )
            rec._guarded().write(
                {"state": "active", "approved_by_id": self.env.uid, "approved_on": c.today(rec.env)}
            )
            rec.message_post(body="Activated by %s." % self.env.user.name)
        return True

    def action_reopen(self):
        c.require_group(self.env, c.G_HSE, "E-Waste HSE Officer", "reopen a collection point")
        for rec in self:
            if rec.state != "active":
                raise UserError("Only an active collection point is reopened.")
            rec._guarded().write({"state": "draft", "approved_by_id": False, "approved_on": False})
        return True

    def action_close(self):
        c.require_group(self.env, c.G_HSE, "E-Waste HSE Officer", "close a collection point")
        for rec in self:
            if rec.state == "closed":
                continue
            stored = (
                self.env["fix.ewaste.battery"]
                .sudo()
                .search_count([("collection_point_id", "=", rec.id), ("state", "=", "stored")])
            )
            if rec.held_kg > 0 or stored:
                raise UserError(
                    "%s still holds e-waste (%.1f kg, %d hazardous record(s)): move it first."
                    % (rec.name, rec.held_kg, stored)
                )
            rec._guarded().write({"state": "closed", "active_to": c.today(rec.env)})
        return True


class FixEwasteCollectionPointLimit(models.Model):
    """One hazardous class a collection point may hold, and its ceiling (T-06)."""

    _name = "fix.ewaste.collection.point.limit"
    _description = "E-Waste Collection Point Hazardous Ceiling"
    _order = "point_id, hazard_class"

    point_id = fields.Many2one(
        "fix.ewaste.collection.point", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="point_id.company_id", store=True)
    hazard_class = fields.Selection(HAZ_CLASSES, required=True)
    max_kg = fields.Float(string="Ceiling (kg)", required=True)
    held_kg = fields.Float(string="Held Now (kg)", compute="_compute_held")

    _one_per_class = models.Constraint(
        "UNIQUE (point_id, hazard_class)", "One ceiling per hazardous class and point"
    )
    _ceiling_positive = models.Constraint("CHECK (max_kg > 0)", "A ceiling is positive")

    def _compute_held(self):
        Bat = self.env["fix.ewaste.battery"].sudo()
        for rec in self:
            held = Bat.search(
                [
                    ("collection_point_id", "=", rec.point_id.id or 0),
                    ("hazmat_class", "=", rec.hazard_class),
                    ("state", "=", "stored"),
                ]
            )
            rec.held_kg = round(sum(held.mapped("weight_kg")), 3)

    def _fix_check_point_open(self, points):
        if self.env.su:
            return
        for point in points:
            if point.state != "draft":
                raise UserError(
                    "%s is %s: an HSE officer reopens it to change its ceilings."
                    % (point.name, point.state)
                )

    @api.model_create_multi
    def create(self, vals_list):
        points = self.env["fix.ewaste.collection.point"].browse(
            [v.get("point_id") for v in vals_list if v.get("point_id")]
        )
        self._fix_check_point_open(points)
        return super().create(vals_list)

    def write(self, vals):
        self._fix_check_point_open(self.mapped("point_id"))
        return super().write(vals)

    def unlink(self):
        self._fix_check_point_open(self.mapped("point_id"))
        return super().unlink()


# ============================================================ p1 receipt
class FixEwasteCollectionCapture(models.Model):
    _inherit = "fix.ewaste.collection"

    channel = fields.Selection(
        [
            ("branch_dropoff", "Branch Drop-off"),
            ("booked_pickup", "Booked Collection"),
            ("corporate", "Corporate Decommission"),
            ("internal_writeoff", "Internal Write-off"),
            ("service_unrepairable", "Unrepairable Service Outcome"),
            ("refurb_failed", "Failed Refurbishment (M14)"),
            ("rental_retired", "Retired Rental Fleet (M13)"),
            ("public_drive", "Public Collection Drive"),
            ("backlog", "Pre-implementation Backlog"),
        ],
        string="Collection Channel",
        required=True,
        default="branch_dropoff",
        index=True,
    )
    condition = fields.Selection(
        [
            ("working", "Working"),
            ("faulty", "Faulty"),
            ("dead", "Dead / No Power"),
            ("damaged", "Physically Damaged"),
            ("swollen", "Swollen / Leaking Battery"),
        ],
        string="Condition on Receipt",
    )
    has_battery = fields.Boolean(string="Contains Battery")
    has_crt = fields.Boolean(string="Contains CRT Glass")
    has_mercury = fields.Boolean(string="Contains Mercury Lamp")
    has_refrigerant = fields.Boolean(string="Contains Refrigerant")
    has_toner = fields.Boolean(string="Contains Toner / Ink")
    photo_attachment_id = fields.Many2one(
        "ir.attachment", string="Receipt Photo", ondelete="restrict", copy=False
    )
    photo_file = fields.Binary(string="Upload Receipt Photo", store=False)
    photo_filename = fields.Char(string="Photo File Name", store=False)
    collection_point_id = fields.Many2one(
        "fix.ewaste.collection.point", string="Collection Point", ondelete="restrict", index=True
    )
    corporate_line_id = fields.Many2one(
        "fix.ewaste.corporate.disposal.line",
        string="Declared Corporate Asset",
        ondelete="restrict",
        copy=False,
    )
    corporate_disposal_id = fields.Many2one(
        related="corporate_line_id.disposal_id", store=True, string="Corporate Disposal"
    )
    donation_ids = fields.One2many("fix.ewaste.donation", "collection_id", string="Donations")

    _corporate_line_once = models.Constraint(
        "UNIQUE (corporate_line_id)", "One received item per declared corporate asset"
    )

    _UPLOADS = {"photo_attachment_id": ("photo_file", "photo_filename")}

    def _fix_form_locked_fields(self) -> set:
        return c.lock_uploads(set(super()._fix_form_locked_fields()), self._UPLOADS)

    @api.model_create_multi
    def create(self, vals_list):
        staged = c.stage_uploads(vals_list, self._UPLOADS)
        for vals in vals_list:
            if vals.get("corporate_line_id"):
                vals.setdefault("channel", "corporate")
                self._fix_check_line_free(vals["corporate_line_id"])
        recs = super().create(vals_list)
        recs._fix_check_receipt()
        c.attach_staged(recs, staged)
        return recs

    def write(self, vals):
        vals = c.lift_uploads(self, vals, self._UPLOADS)
        if vals.get("corporate_line_id"):
            self._fix_check_line_free(vals["corporate_line_id"], exclude=self)
        res = super().write(vals)
        if {"collection_point_id", "corporate_line_id", "customer_id", "weight_kg"} & set(vals):
            self._fix_check_receipt()
        return res

    def _fix_check_line_free(self, line_id, exclude=None):
        """One received item per declared asset, refused with a reason (the
        UNIQUE constraint is the backstop)."""
        if exclude is not None and len(exclude) > 1:
            raise UserError("Book one item against a declared asset at a time.")
        taken = self.sudo().search(
            [("corporate_line_id", "=", line_id), ("id", "not in", (exclude or self.browse()).ids)],
            limit=1,
        )
        if taken:
            line = self.env["fix.ewaste.corporate.disposal.line"].sudo().browse(line_id)
            raise UserError(
                "Declared asset %s is already received as %s." % (line.asset_ref, taken.name)
            )

    def _fix_check_receipt(self):
        """Received only at an active point; a corporate asset only from its
        contract's client while the contract is receiving (FR-ESG-005/022)."""
        for rec in self:
            point = rec.sudo().collection_point_id
            if point and point.state != "active" and rec.state == "collected":
                raise UserError(
                    "%s is %s: e-waste is received only at an active collection point."
                    % (point.name, point.state)
                )
            line = rec.sudo().corporate_line_id
            if line:
                disposal = line.disposal_id
                if disposal.state != "receiving":
                    raise UserError(
                        "Corporate disposal %s is %s: its assets are received only while it "
                        "is receiving." % (disposal.name, disposal.state)
                    )
                if rec.customer_id != disposal.client_id:
                    raise UserError(
                        "Declared asset %s belongs to %s, not %s."
                        % (line.asset_ref, disposal.client_id.name, rec.customer_id.name)
                    )
            if point and point.capacity_kg and point.held_kg > point.capacity_kg + 1e-6:
                c.notify(
                    point,
                    "Collection point over capacity",
                    "%s holds %.1f kg against a capacity of %.1f kg: schedule a transfer."
                    % (point.name, point.held_kg, point.capacity_kg),
                    c.G_HSE,
                )

    # ------------------------------------------------------------ hazmat
    _FLAG_FRACTIONS = (
        ("has_battery", "li_ion"),
        ("has_crt", "crt"),
        ("has_mercury", "mercury_lamp"),
        ("has_refrigerant", "refrigerant"),
        ("has_toner", "toner"),
    )

    def _fix_open_hazmat(self):
        """A hazardous item opens one hazmat record per hazard flagged at
        receipt (FR-ESG-015); the first carries the item's weight, the HSE
        officer weighs the others before the inspection freezes them."""
        Battery = self.env["fix.ewaste.battery"].sudo()
        for rec in self:
            if rec.battery_ids:
                continue
            fractions = [chem for flag, chem in self._FLAG_FRACTIONS if rec[flag]]
            if rec.material_type == "battery" and "li_ion" not in fractions:
                fractions.insert(0, "li_ion")
            if not fractions:
                # graded hazardous with no flag ticked: one record of an
                # unspecified fraction, placed (or refused) like any other
                fractions = ["other"]
            swollen = rec.condition == "swollen"
            for n, chem in enumerate(fractions):
                hclass = _hazard_class(chem, swollen and chem == "li_ion")
                weight = (rec.weight_kg or 0.0) if n == 0 else 0.0
                point = rec.sudo().collection_point_id
                refusal = rec._fix_point_refusal(point, hclass, weight)
                bat = Battery.create(
                    {
                        "collection_id": rec.id,
                        "company_id": rec.company_id.id,
                        "operating_unit_id": rec.operating_unit_id.id or False,
                        "chemistry": chem,
                        "swollen_cell": swollen and chem == "li_ion",
                        "weight_kg": weight,
                        "collection_point_id": point.id if point and not refusal else False,
                    }
                )
                if refusal:
                    bat._fix_alert_ceiling(point, hclass, weight, refusal)
            rec.invalidate_recordset(["battery_ids"])
        return super()._fix_open_hazmat()

    def _fix_point_refusal(self, point, hclass, weight):
        """M18-12 (BRU-ESG-07, T-06): why the item's point may NOT accept this
        hazmat class and weight, or '' when it may. A hazmat item is accepted
        only at an active point with a ceiling for its class, within it."""
        self.ensure_one()
        label = dict(HAZ_CLASSES).get(hclass, hclass)
        if not point:
            return "it was received at no designated collection point"
        if point.state != "active":
            return "%s is %s" % (point.name, point.state)
        limit = point._fix_limit_for(hclass)
        if not limit:
            return "%s is not designated for %s (no ceiling for the class)" % (point.name, label)
        held = sum(
            self.env["fix.ewaste.battery"]
            .sudo()
            .search(
                [
                    ("collection_point_id", "=", point.id),
                    ("hazmat_class", "=", hclass),
                    ("state", "=", "stored"),
                ]
            )
            .mapped("weight_kg")
        )
        if held + weight > limit.max_kg + 1e-6:
            return "%s would hold %.1f kg of %s against its %.1f kg ceiling" % (
                point.name,
                held + weight,
                label,
                limit.max_kg,
            )
        return ""

    # ------------------------------------------------------------ routes
    def action_route_harvest(self):
        """FR-ESG-008: a unit triaged for parts harvesting goes to M14, which
        harvests it into M15 stock. The M06 gate runs in write()."""
        c.require_group(
            self.env, c.G_ASSESSOR, "E-Waste Triage Assessor", "route a unit for harvesting"
        )
        for rec in self:
            if rec.state != "triaged" or rec.triage_grade != "harvest":
                raise UserError("%s is not triaged for parts harvesting." % rec.name)
            rec._fix_route_to_refurbishment()
        return True

    def _fix_check_donation_gate(self, grade):
        """BRU-ESG-15: a donation leaves under the same gate as any route."""
        self.ensure_one()
        if grade != "donate":
            raise UserError("%s is not triaged for donation." % self.name)
        donation = self.sudo().donation_ids.filtered(
            lambda d: d.state == "approved" and d.acknowledgement_attachment_id
        )
        if not donation:
            raise UserError(
                "%s leaves as a donation only under an approved donation with the "
                "recipient's signed acknowledgement." % self.name
            )
        denial = self._fix_wipe_denial()
        if denial:
            raise UserError(
                "%s cannot be donated: it needs a verified M06 certificate bound to it "
                "(%s)." % (self.name, denial)
            )

    @api.model
    def consume_tradein_harvested(self, event):
        col = super().consume_tradein_harvested(event)
        if col and col.channel != "refurb_failed":
            col.sudo()._guarded().write({"channel": "refurb_failed"})
        return col

    @api.model
    def consume_stock_written_off(self, event):
        col = super().consume_stock_written_off(event)
        if col and col.channel != "internal_writeoff":
            col.sudo()._guarded().write({"channel": "internal_writeoff"})
        return col

    # ------------------------------------------------------------ I1 (M13)
    @api.model
    def consume_rental_asset_retired(self, event):
        """I1 (S1 -> S3): rental.asset_retired with route 'recycle' -> an
        e-waste collection carrying the unit's device, serial, weight,
        material and operating unit (M18-14: the M13 route was a manual tick
        that lost all of them). Superuser-only (the event relay) and
        idempotent: one collection per retired asset. The asset is re-read:
        it must exist and be retired; the payload is used only for what the
        asset itself does not hold. A 'resale' route is M14's (S2), not ours.
        The unit then goes through M18's own triage, wipe and dispatch gates."""
        if not self.env.su:
            raise UserError("consume_rental_asset_retired runs only from the event relay.")
        payload = event.get("payload") or {}
        if event.get("aggregate") not in (None, "fix.rental.asset"):
            return self.browse()
        if "fix.rental.asset" not in self.env:
            return self.browse()
        try:
            asset_id = int(event.get("aggregate_id") or payload.get("asset_id") or 0)
        except (TypeError, ValueError):
            asset_id = 0
        asset = self.env["fix.rental.asset"].sudo().browse(asset_id).exists() if asset_id else None
        if not asset:
            raise UserError("Rental retirement refused: no fix.rental.asset #%s." % asset_id)

        # the retirement record (S1) holds the route, weight and material;
        # the payload only fills what no record holds
        retirement = (
            self.env["fix.rental.retirement"]
            .sudo()
            .search(
                [("asset_id", "=", asset.id), ("state", "=", "retired")], order="id desc", limit=1
            )
            if "fix.rental.retirement" in self.env
            else None
        )

        def own(name, fallback=None):
            for rec in (retirement, asset):
                if rec and name in rec._fields and rec[name]:
                    return rec[name]
            return fallback

        route = own("route", payload.get("route"))
        if route != "recycle":
            return self.browse()
        if "status" in asset._fields and asset.status != "retired":
            raise UserError(
                "Rental retirement refused: %s is %s, not retired." % (asset.name, asset.status)
            )
        device = (
            own("device_id")
            or self.env["fix.device"].sudo().browse(int(payload.get("device_id") or 0)).exists()
        )
        materials = dict(self._fields["material_type"].selection)
        material = own("material", payload.get("material"))
        if material not in materials:
            material = (
                self._DEVICE_MATERIAL.get(device.device_type, "other")
                if device and "device_type" in device._fields
                else "other"
            )
        try:
            weight = float(own("weight_kg", payload.get("weight_kg")) or 0.0)
        except (TypeError, ValueError):
            weight = 0.0
        existing = self._fix_unit_collection(asset, device)
        if existing:
            # one collection per unit: the M49 disposal hand-off may have
            # received it first (lead note, S1 report) - link, never duplicate
            return existing._fix_link_rental_source(asset, weight=weight, material=material)
        company = asset.company_id if "company_id" in asset._fields else self.env.company
        ou = (
            own("operating_unit_id")
            or self.env["operating.unit"]
            .sudo()
            .browse(int(payload.get("operating_unit_id") or 0))
            .exists()
        )
        col = (
            self.sudo()
            ._guarded()
            .create(
                {
                    "company_id": company.id,
                    "operating_unit_id": ou.id if ou else False,
                    # a retired fleet unit is the company's own
                    "customer_id": company.partner_id.id,
                    "device_id": device.id if device else False,
                    "material_type": material,
                    "weight_kg": max(weight, 0.0),
                    "channel": "rental_retired",
                    "source_model": asset._name,
                    "source_res_id": asset.id,
                    "source_ref": asset.name,
                }
            )
        )
        serial = payload.get("serial") or (device.serial_number if device else "")
        col.message_post(
            body="Received from M13: retired rental unit %s%s, %.3f kg%s."
            % (
                asset.name,
                " (serial %s)" % serial if serial else "",
                col.weight_kg,
                "" if col.weight_kg > 0 else " - weigh it in before triage",
            )
        )
        # never hand back a record that still carries the guard token
        return self.browse(col.id)


class FixEwasteBatteryCapture(models.Model):
    _inherit = "fix.ewaste.battery"

    collection_point_id = fields.Many2one(
        "fix.ewaste.collection.point", string="Storage Point", ondelete="restrict", index=True
    )
    hazmat_class = fields.Selection(
        HAZ_CLASSES,
        string="Ceiling Class",
        compute="_compute_hazmat_class",
        store=True,
        index=True,
    )

    @api.depends("chemistry", "swollen_cell")
    def _compute_hazmat_class(self):
        for rec in self:
            rec.hazmat_class = _hazard_class(rec.chemistry, rec.swollen_cell)

    def _fix_alert_ceiling(self, point, hclass, weight, reason):
        """M18-12: the item was NOT accepted at the point - it waits, unplaced
        (no inspection, no dispatch), and the HSE officer is alerted and
        ewaste.hazmat_ceiling_breach published for M59 / M47."""
        for rec in self:
            label = dict(HAZ_CLASSES).get(hclass, hclass)
            limit = point._fix_limit_for(hclass) if point else None
            publish(
                rec.env,
                "ewaste.hazmat_ceiling_breach",
                "fix.ewaste.battery",
                rec.id,
                {
                    "location": point.name if point else None,
                    "point_id": point.id if point else None,
                    "hazard_class": hclass,
                    "quantity_kg": weight,
                    "ceiling_kg": limit.max_kg if limit else None,
                    "reason": reason,
                    "company_id": rec.company_id.id,
                },
            )
            # a to-do for the HSE officer on the item (the hazmat record has
            # no activities), the refusal on the hazmat record's own chatter
            rec.message_post(
                body="Not accepted at %s: %s." % (point.name if point else "-", reason)
            )
            c.notify(
                rec.collection_id or rec,
                "Hazmat not accepted at its point",
                "%s (%s, %.3f kg) was not accepted: %s. Place it at a point designated, with "
                "room, for %s before it is inspected or dispatched (BRU-ESG-07)."
                % (rec.name, label, weight, reason, label),
                c.G_HSE,
            )

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(r.state != "stored" for r in self):
            locked.add("collection_point_id")
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        Point = self.env["fix.ewaste.collection.point"].sudo()
        for vals in vals_list:
            if vals.get("collection_point_id") and not vals.get("storage_location"):
                vals["storage_location"] = Point.browse(vals["collection_point_id"]).name
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open() and "collection_point_id" in vals:
            for rec in self:
                if rec.state != "stored" and c.changed_fields(rec, vals, {"collection_point_id"}):
                    c.frozen_refuse(rec, {"collection_point_id"}, "has left storage")
        if vals.get("collection_point_id") and "storage_location" not in vals:
            vals = dict(vals)
            point = (
                self.env["fix.ewaste.collection.point"].sudo().browse(vals["collection_point_id"])
            )
            vals["storage_location"] = point.name
        res = super().write(vals)
        if {"collection_point_id", "chemistry", "swollen_cell"} & set(vals):
            self._check_location_ceiling()
        return res

    def _check_location_ceiling(self):
        """T-06 / BRU-ESG-07: at a designated point the ceiling is per class;
        a point holds only the classes it has a ceiling for. Records without a
        point keep the company-wide ceiling per storage location."""
        pointed = self.filtered("collection_point_id")
        super(FixEwasteBatteryCapture, self - pointed)._check_location_ceiling()
        Bat = self.sudo()
        for point, hclass in {(r.collection_point_id, r.hazmat_class) for r in pointed}:
            point = point.sudo()
            if point.state != "active":
                raise ValidationError(
                    "%s is %s: hazardous material is stored only at an active point."
                    % (point.name, point.state)
                )
            limit = point._fix_limit_for(hclass)
            label = dict(HAZ_CLASSES).get(hclass, hclass)
            if not limit:
                raise ValidationError(
                    "%s is not designated for %s: an HSE officer sets a ceiling for that "
                    "class first (BRU-ESG-07)." % (point.name, label)
                )
            held = Bat.search(
                [
                    ("collection_point_id", "=", point.id),
                    ("hazmat_class", "=", hclass),
                    ("state", "=", "stored"),
                ]
            )
            total = sum(held.mapped("weight_kg"))
            if total > limit.max_kg + 1e-6:
                raise ValidationError(
                    "%s would hold %.1f kg of %s; its ceiling is %.1f kg (T-06)."
                    % (point.name, total, label, limit.max_kg)
                )


# ============================================================ p1 corporate
class FixEwasteCorporateDisposal(models.Model):
    """Contracted bulk disposal (FR-ESG-005): the client's declared asset
    list, each asset reconciled to the item received and its certificate.
    Not closed while any declared asset is unreconciled (BRU-ESG-14)."""

    _name = "fix.ewaste.corporate.disposal"
    _description = "E-Waste Corporate Disposal Contract"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(required=True, default="New", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    client_id = fields.Many2one("res.partner", string="Corporate Client", required=True)
    contract_ref = fields.Char(string="Contract / PO Reference")
    account_manager_id = fields.Many2one("res.users", string="Account Manager")
    line_ids = fields.One2many(
        "fix.ewaste.corporate.disposal.line", "disposal_id", string="Declared Assets"
    )
    declared_count = fields.Integer(compute="_compute_counts")
    received_count = fields.Integer(compute="_compute_counts")
    reconciled_count = fields.Integer(compute="_compute_counts")
    open_count = fields.Integer(string="Unreconciled", compute="_compute_counts")
    state = fields.Selection(
        [("draft", "Draft"), ("receiving", "Receiving"), ("closed", "Closed")],
        required=True,
        default="draft",
        tracking=True,
    )
    confirmed_by_id = fields.Many2one("res.users", readonly=True)
    closed_by_id = fields.Many2one("res.users", readonly=True)
    closed_on = fields.Date(readonly=True)
    notes = fields.Text()

    _TERMS = frozenset({"client_id", "contract_ref", "company_id"})

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | {
            "state",
            "confirmed_by_id",
            "closed_by_id",
            "closed_on",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(r.state != "draft" for r in self):
            locked |= self._TERMS
        if self and any(r.state == "closed" for r in self):
            locked |= {"line_ids", "account_manager_id"}
        return locked

    @api.depends("line_ids.line_state")
    def _compute_counts(self):
        for rec in self:
            lines = rec.line_ids
            rec.declared_count = len(lines)
            rec.received_count = len(lines.filtered(lambda x: x.line_state != "declared"))
            done = lines.filtered(lambda x: x.line_state in ("reconciled", "exception"))
            rec.reconciled_count = len(done)
            rec.open_count = len(lines) - len(done)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = _seq(self.env, "fix.ewaste.corporate.disposal", "ECD/New")
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                if rec.state != "draft":
                    changed = c.changed_fields(rec, vals, self._TERMS)
                    if changed:
                        c.frozen_refuse(rec, changed, "is %s" % rec.state)
                if rec.state == "closed" and "line_ids" in vals:
                    c.frozen_refuse(rec, {"line_ids"}, "is closed")
        return super().write(vals)

    def action_confirm(self):
        """The declared list is complete: receiving starts, the list freezes."""
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is not a draft." % rec.name)
            if not rec.line_ids:
                raise UserError("%s declares no asset: list the client's assets first." % rec.name)
            rec._guarded().write({"state": "receiving", "confirmed_by_id": self.env.uid})
        return True

    def action_close(self):
        c.require_group(
            self.env, c.G_COMPLIANCE, "E-Waste Compliance Officer", "close a corporate disposal"
        )
        for rec in self:
            if rec.state != "receiving":
                raise UserError("%s is not receiving." % rec.name)
            pending = rec.line_ids.filtered(
                lambda x: x.line_state not in ("reconciled", "exception")
            )
            if pending:
                raise UserError(
                    "%s cannot close: %d declared asset(s) are not reconciled to a certificate "
                    "or a documented exception (BRU-ESG-14): %s"
                    % (rec.name, len(pending), ", ".join(pending[:10].mapped("asset_ref")))
                )
            rec._guarded().write(
                {"state": "closed", "closed_by_id": self.env.uid, "closed_on": c.today(rec.env)}
            )
            rec.message_post(
                body="Closed by %s: %d declared, %d reconciled, %d documented exception(s)."
                % (
                    self.env.user.name,
                    rec.declared_count,
                    len(rec.line_ids.filtered(lambda x: x.line_state == "reconciled")),
                    len(rec.line_ids.filtered(lambda x: x.line_state == "exception")),
                )
            )
        return True


class FixEwasteCorporateDisposalLine(models.Model):
    """One declared asset of a corporate disposal and its reconciliation."""

    _name = "fix.ewaste.corporate.disposal.line"
    _description = "E-Waste Corporate Disposal - Declared Asset"
    _inherit = ["fix.guarded.mixin"]
    _order = "disposal_id, id"
    _rec_name = "asset_ref"

    disposal_id = fields.Many2one(
        "fix.ewaste.corporate.disposal", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="disposal_id.company_id", store=True)
    asset_ref = fields.Char(string="Asset Tag / Serial", required=True)
    description = fields.Char()
    material_type = fields.Selection(MATERIALS, default="laptop")
    collection_ids = fields.One2many("fix.ewaste.collection", "corporate_line_id")
    collection_id = fields.Many2one(
        "fix.ewaste.collection", string="Received Item", compute="_compute_received_item"
    )
    line_state = fields.Selection(
        [
            ("declared", "Declared - Not Received"),
            ("received", "Received - In Process"),
            ("reconciled", "Reconciled to Certificate"),
            ("exception", "Documented Exception"),
        ],
        string="Reconciliation",
        compute="_compute_line_state",
        store=True,
    )
    exception_reason = fields.Text()
    exception_by_id = fields.Many2one("res.users", string="Exception Accepted By", readonly=True)
    exception_on = fields.Date(readonly=True)

    _GUARDED = frozenset({"exception_by_id", "exception_on"})
    _DECLARED = frozenset({"disposal_id", "asset_ref", "description", "material_type"})

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | self._GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(r.disposal_id.state != "draft" for r in self):
            locked |= self._DECLARED
        if self and any(r.exception_by_id or r.line_state == "reconciled" for r in self):
            locked.add("exception_reason")
        return locked

    @api.depends("collection_ids")
    def _compute_received_item(self):
        for rec in self:
            rec.collection_id = rec.collection_ids[:1]

    @api.depends(
        "collection_ids.state",
        "collection_ids.wipe_certificate_id",
        "exception_by_id",
    )
    def _compute_line_state(self):
        for rec in self:
            col = rec.collection_ids[:1]
            if rec.exception_by_id:
                rec.line_state = "exception"
            elif not col:
                rec.line_state = "declared"
            elif col.state in _RECONCILED or (
                col.state == "routed" and not col.sudo()._fix_wipe_denial()
            ):
                rec.line_state = "reconciled"
            else:
                rec.line_state = "received"

    def _fix_check_open(self, disposals):
        if self.env.su:
            return
        for disposal in disposals:
            if disposal.state != "draft":
                raise UserError(
                    "%s is %s: its declared asset list no longer changes."
                    % (disposal.name, disposal.state)
                )

    @api.model_create_multi
    def create(self, vals_list):
        self._fix_check_open(
            self.env["fix.ewaste.corporate.disposal"].browse(
                [v["disposal_id"] for v in vals_list if v.get("disposal_id")]
            )
        )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            if self._DECLARED & set(vals):
                for rec in self:
                    if c.changed_fields(rec, vals, self._DECLARED):
                        self._fix_check_open(rec.disposal_id)
            if "exception_reason" in vals:
                for rec in self:
                    if (rec.exception_by_id or rec.line_state == "reconciled") and c.changed_fields(
                        rec, vals, {"exception_reason"}
                    ):
                        c.frozen_refuse(rec, {"exception_reason"}, "is settled")
        return super().write(vals)

    def unlink(self):
        self._fix_check_open(self.mapped("disposal_id"))
        return super().unlink()

    def action_accept_exception(self, reason=None):
        """A declared asset that will not be reconciled (never handed over,
        lost in custody) is closed only on a documented, accepted reason."""
        c.require_group(
            self.env, c.G_COMPLIANCE, "E-Waste Compliance Officer", "accept a disposal exception"
        )
        if reason and str(reason).strip():
            self.write({"exception_reason": str(reason).strip()})
        for rec in self:
            if rec.disposal_id.state != "receiving":
                raise UserError("%s is not receiving." % rec.disposal_id.name)
            if rec.line_state in ("reconciled", "exception"):
                raise UserError("Asset %s is already settled." % rec.asset_ref)
            if not (rec.exception_reason or "").strip():
                raise UserError("Document why asset %s is an exception first." % rec.asset_ref)
            rec._guarded().write(
                {"exception_by_id": self.env.uid, "exception_on": c.today(rec.env)}
            )
            rec.disposal_id.message_post(
                body="Asset %s accepted as an exception by %s: %s"
                % (rec.asset_ref, self.env.user.name, rec.exception_reason)
            )
        return True


# ============================================================ p2 criteria
class FixEwasteTriageCriteria(models.Model):
    """The published triage criteria (FR-ESG-006): versioned, written by one
    compliance officer and published by another; the version in force is
    stamped on every decision (FR-ESG-007). Once published it never changes:
    a change is a new version, which retires the old one."""

    _name = "fix.ewaste.triage.criteria"
    _description = "E-Waste Triage Criteria"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "company_id, effective_from desc, id desc"

    name = fields.Char(string="Version", required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    effective_from = fields.Date(default=fields.Date.context_today)
    reuse_criteria = fields.Text(string="Reuse / Refurbish when")
    harvest_criteria = fields.Text(string="Harvest Parts when")
    recycle_criteria = fields.Text(string="Recycle when")
    hazardous_criteria = fields.Text(string="Hazardous Treatment when")
    donation_max_value = fields.Float(
        string="Donation: Max Market Value (BDT)",
        help="A device is donated only if fully functional and worth at most this much "
        "(functional low-value devices, FR-ESG-023).",
    )
    evidence_required = fields.Boolean(
        string="Photo Evidence Required", default=True, help="BRU-ESG-09"
    )
    state = fields.Selection(
        [("draft", "Draft"), ("active", "In Force"), ("retired", "Retired")],
        required=True,
        default="draft",
    )
    published_by_id = fields.Many2one("res.users", readonly=True)
    published_on = fields.Date(readonly=True)
    retired_on = fields.Date(readonly=True)

    _version_once = models.Constraint(
        "UNIQUE (company_id, name)", "Each criteria version is published once"
    )

    _TEXT = frozenset(
        {
            "name",
            "company_id",
            "effective_from",
            "reuse_criteria",
            "harvest_criteria",
            "recycle_criteria",
            "hazardous_criteria",
            "donation_max_value",
            "evidence_required",
        }
    )

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | {
            "state",
            "published_by_id",
            "published_on",
            "retired_on",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(r.state != "draft" for r in self):
            locked |= self._TEXT
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            c.require_group(
                self.env, c.G_COMPLIANCE, "E-Waste Compliance Officer", "write triage criteria"
            )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                if rec.state != "draft":
                    changed = c.changed_fields(rec, vals, self._TEXT)
                    if changed:
                        c.frozen_refuse(rec, changed, "is published (write a new version)")
        return super().write(vals)

    @api.model
    def _fix_in_force(self, company):
        return self.sudo().search(
            [("company_id", "=", company.id), ("state", "=", "active")], limit=1
        )

    def _fix_check_assessment(self, vals, has_evidence):
        """The assessment a decision must carry under these criteria."""
        if not self:
            return
        self.ensure_one()
        if not vals.get("functional_result"):
            raise UserError(
                "Criteria %s are in force: record the functional test result." % self.name
            )
        if self.evidence_required and not has_evidence:
            raise UserError(
                "Criteria %s require photo evidence of the assessment (BRU-ESG-09)." % self.name
            )
        decision = vals.get("decision")
        if decision in ("reuse", "donate") and vals.get("functional_result") != "pass":
            raise UserError("Only a fully functional device is reused or donated.")
        if decision == "donate":
            value = vals.get("market_value_estimate") or 0.0
            if value <= 0 or value > self.donation_max_value:
                raise UserError(
                    "A donation is a functional LOW-VALUE device: estimate its value "
                    "(at most %.0f BDT under criteria %s)." % (self.donation_max_value, self.name)
                )

    def action_publish(self):
        c.require_group(
            self.env, c.G_COMPLIANCE, "E-Waste Compliance Officer", "publish triage criteria"
        )
        today = c.today(self.env)
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is not a draft." % rec.name)
            if not self.env.su and rec.create_uid == self.env.user:
                raise UserError("You wrote %s: another compliance officer publishes it." % rec.name)
            if not all(
                (rec[f] or "").strip()
                for f in (
                    "reuse_criteria",
                    "harvest_criteria",
                    "recycle_criteria",
                    "hazardous_criteria",
                )
            ):
                raise UserError("%s states a criterion for every route first." % rec.name)
            previous = self.sudo().search(
                [("company_id", "=", rec.company_id.id), ("state", "=", "active")]
            )
            previous._guarded().write({"state": "retired", "retired_on": today})
            rec._guarded().write(
                {"state": "active", "published_by_id": self.env.uid, "published_on": today}
            )
        return True


# ============================================================ p2 donation
class FixEwasteDonation(models.Model):
    """A functional low-value device given to a donation recipient
    (FR-ESG-023): approved by a compliance officer who did not raise it, and
    handed over only under the M06 gate with the recipient's signed
    acknowledgement (BRU-ESG-15)."""

    _name = "fix.ewaste.donation"
    _description = "E-Waste Donation"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(required=True, default="New", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    collection_id = fields.Many2one(
        "fix.ewaste.collection", string="Item", required=True, ondelete="restrict", index=True
    )
    recipient_id = fields.Many2one("res.partner", string="Recipient", required=True)
    recipient_reg_no = fields.Char(
        string="Recipient Registration No",
        help="NGO Affairs Bureau / Department of Social Services registration of the recipient.",
    )
    purpose = fields.Char()
    acknowledgement_attachment_id = fields.Many2one(
        "ir.attachment", string="Signed Acknowledgement", ondelete="restrict"
    )
    acknowledgement_file = fields.Binary(string="Upload Signed Acknowledgement", store=False)
    acknowledgement_filename = fields.Char(string="Acknowledgement File Name", store=False)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("approved", "Approved"),
            ("handed_over", "Handed Over"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="draft",
        tracking=True,
    )
    approved_by_id = fields.Many2one("res.users", readonly=True)
    approved_on = fields.Date(readonly=True)
    handed_over_by_id = fields.Many2one("res.users", readonly=True)
    handed_over_on = fields.Date(readonly=True)
    notes = fields.Text()

    _TERMS = frozenset({"collection_id", "recipient_id", "recipient_reg_no", "company_id"})
    _UPLOADS = {
        "acknowledgement_attachment_id": ("acknowledgement_file", "acknowledgement_filename")
    }

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | {
            "state",
            "approved_by_id",
            "approved_on",
            "handed_over_by_id",
            "handed_over_on",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(r.state != "draft" for r in self):
            locked |= self._TERMS
        if self and any(r.state != "approved" for r in self):
            locked.add("acknowledgement_attachment_id")
        if not self:
            locked.add("acknowledgement_attachment_id")
        return c.lock_uploads(locked, self._UPLOADS)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            data = vals.pop("acknowledgement_file", None)
            vals.pop("acknowledgement_filename", None)
            if data or vals.get("acknowledgement_attachment_id"):
                raise UserError(
                    "The signed acknowledgement is attached once the donation is approved."
                )
            if vals.get("name", "New") == "New":
                vals["name"] = _seq(self.env, "fix.ewaste.donation", "EDON/New")
            col = self.env["fix.ewaste.collection"].sudo().browse(vals.get("collection_id"))
            if not col.exists() or col.state != "triaged" or col.triage_grade != "donate":
                raise UserError("Only an item triaged for donation is donated.")
            live = col.donation_ids.filtered(lambda d: d.state != "cancelled")
            if live:
                raise UserError("%s already has donation %s." % (col.name, live[0].name))
            vals.setdefault("company_id", col.company_id.id)
        return super().create(vals_list)

    def write(self, vals):
        vals = c.lift_uploads(self, vals, self._UPLOADS)
        if self and not self._fix_guard_open():
            for rec in self:
                names = set(self._TERMS) if rec.state != "draft" else set()
                if rec.state != "approved":
                    names.add("acknowledgement_attachment_id")
                changed = c.changed_fields(rec, vals, names)
                if changed:
                    c.frozen_refuse(rec, changed, "is %s" % rec.state)
        return super().write(vals)

    def action_approve(self):
        c.require_group(
            self.env, c.G_COMPLIANCE, "E-Waste Compliance Officer", "approve a donation"
        )
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is not a draft." % rec.name)
            if not self.env.su and rec.create_uid == self.env.user:
                raise UserError("You raised %s: another compliance officer approves it." % rec.name)
            if not (rec.recipient_reg_no or "").strip():
                raise UserError("Record the recipient's registration number first.")
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.uid,
                    "approved_on": c.today(rec.env),
                }
            )
        return True

    def action_hand_over(self):
        """Custody passes to the recipient: the M06 gate runs on the item."""
        c.require_group(self.env, c.G_DISPATCH, "E-Waste Dispatcher", "hand over a donation")
        for rec in self:
            if rec.state != "approved":
                raise UserError("%s is not approved." % rec.name)
            if not rec.acknowledgement_attachment_id:
                raise UserError("Attach the recipient's signed acknowledgement first.")
            rec.collection_id._guarded().write({"state": "donated"})
            rec._guarded().write(
                {
                    "state": "handed_over",
                    "handed_over_by_id": self.env.uid,
                    "handed_over_on": c.today(rec.env),
                }
            )
            rec.collection_id.message_post(
                body="Donated to %s under %s." % (rec.recipient_id.name, rec.name)
            )
        return True

    def action_cancel(self):
        for rec in self:
            if rec.state not in ("draft", "approved"):
                raise UserError("%s is %s: it is not cancelled." % (rec.name, rec.state))
            rec._guarded().write({"state": "cancelled"})
        return True


# ============================================================ p4 downstream
class FixEwastePartnerDownstream(models.Model):
    """A recycler's declared onward destination for a material stream
    (FR-ESG-024, R2v3 downstream due diligence): declared at qualification,
    verified by a recycler approver who did not declare it, at least
    annually (BRU-ESG-18). A dispatch needs a current verified destination
    for its material."""

    _name = "fix.ewaste.partner.downstream"
    _description = "E-Waste Recycler Downstream Vendor"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "partner_id, material_class"

    partner_id = fields.Many2one(
        "fix.ewaste.partner", string="Recycler", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="partner_id.company_id", store=True)
    name = fields.Char(string="Downstream Vendor", required=True)
    material_class = fields.Selection(
        [*MATERIALS, ("all", "All Materials")], required=True, default="all"
    )
    process = fields.Char(string="Onward Process", help="e.g. PCB smelting, plastic regrind")
    country_id = fields.Many2one(
        "res.country",
        string="Country",
        required=True,
        default=lambda self: self.env.ref("base.bd", raise_if_not_found=False),
    )
    licence_ref = fields.Char(string="Vendor Licence / Authorisation")
    declared_on = fields.Date(default=fields.Date.context_today, readonly=True)
    evidence_attachment_id = fields.Many2one(
        "ir.attachment", string="Verification Evidence", ondelete="restrict"
    )
    evidence_file = fields.Binary(string="Upload Verification Evidence", store=False)
    evidence_filename = fields.Char(string="Evidence File Name", store=False)
    verified_on = fields.Date(readonly=True)
    verified_by_id = fields.Many2one("res.users", readonly=True)
    verification_due = fields.Date(compute="_compute_due")
    state = fields.Selection(
        [("declared", "Declared"), ("verified", "Verified"), ("withdrawn", "Withdrawn")],
        required=True,
        default="declared",
    )

    _DECLARED = frozenset({"partner_id", "name", "material_class", "country_id", "process"})
    _UPLOADS = {"evidence_attachment_id": ("evidence_file", "evidence_filename")}

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | {"state", "verified_on", "verified_by_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(r.state != "declared" for r in self):
            locked |= self._DECLARED
        if self and any(r.state == "withdrawn" for r in self):
            locked |= {"evidence_attachment_id", "licence_ref"}
        return c.lock_uploads(locked, self._UPLOADS)

    @api.depends("verified_on")
    def _compute_due(self):
        days = c.param_int(self.env, P_DOWNSTREAM_DAYS, DEFAULT_DOWNSTREAM_DAYS)
        for rec in self:
            rec.verification_due = rec.verified_on and rec.verified_on + timedelta(days=days)

    @api.model_create_multi
    def create(self, vals_list):
        staged = c.stage_uploads(vals_list, self._UPLOADS)
        recs = super().create(vals_list)
        c.attach_staged(recs, staged)
        return recs

    def write(self, vals):
        vals = c.lift_uploads(self, vals, self._UPLOADS)
        if self and not self._fix_guard_open():
            for rec in self:
                names = set(self._DECLARED) if rec.state != "declared" else set()
                if rec.state == "withdrawn":
                    names |= {"evidence_attachment_id", "licence_ref"}
                changed = c.changed_fields(rec, vals, names)
                if changed:
                    c.frozen_refuse(rec, changed, "is %s" % rec.state)
        return super().write(vals)

    def action_verify(self):
        """Verify (or annually re-verify) the destination from evidence."""
        c.require_group(
            self.env,
            c.G_RECYCLER_APPROVER,
            "E-Waste Recycler Approver",
            "verify a downstream vendor",
        )
        for rec in self:
            if rec.state == "withdrawn":
                raise UserError("%s is withdrawn." % rec.name)
            if not self.env.su and rec.create_uid == self.env.user:
                raise UserError("You declared %s: another approver verifies it." % rec.name)
            if not rec.evidence_attachment_id:
                raise UserError("Attach the verification evidence for %s first." % rec.name)
            rec._guarded().write(
                {
                    "state": "verified",
                    "verified_on": c.today(rec.env),
                    "verified_by_id": self.env.uid,
                }
            )
            rec.message_post(body="Verified by %s." % self.env.user.name)
        return True

    def action_withdraw(self):
        """M18-22: withdrawing a recycler's onward destination is a recycler
        approver's or compliance officer's decision, not any user's."""
        if not (
            self.env.su
            or self.env.user.has_group(c.G_RECYCLER_APPROVER)
            or self.env.user.has_group(c.G_COMPLIANCE)
        ):
            raise UserError(
                "Only an E-Waste Recycler Approver or Compliance Officer withdraws a downstream "
                "destination."
            )
        for rec in self:
            if rec.state == "withdrawn":
                continue
            rec._guarded().write({"state": "withdrawn"})
            rec.message_post(body="Withdrawn by %s." % self.env.user.name)
        return True

    def _fix_current(self, today):
        days = c.param_int(self.env, P_DOWNSTREAM_DAYS, DEFAULT_DOWNSTREAM_DAYS)
        return self.filtered(
            lambda r: r.state == "verified"
            and r.verified_on
            and r.verified_on + timedelta(days=days) >= today
        )


class FixEwastePartnerCapture(models.Model):
    _inherit = "fix.ewaste.partner"

    downstream_ids = fields.One2many(
        "fix.ewaste.partner.downstream", "partner_id", string="Downstream Vendors"
    )

    def action_approve_partner(self):
        """BRU-ESG-18: downstream destinations are declared at qualification."""
        self._approval_assert_routed()  # only from the approver's inbox (A05 E11)
        for rec in self:
            if not rec.partner_id:
                # M18-06: a recycler's fee or income is paid to / invoiced on
                # its business contact - qualified only with one
                raise UserError(
                    "Recycler %s has no business contact: link the contact its fees are paid "
                    "to and its income invoiced on before it is qualified." % rec.name
                )
            if not rec.sudo().downstream_ids.filtered(lambda d: d.state != "withdrawn"):
                raise UserError(
                    "Recycler %s has declared no downstream destination: where its material "
                    "goes next is declared before it is qualified (BRU-ESG-18)." % rec.name
                )
        return super().action_approve_partner()


class FixEwasteBatchCapture(models.Model):
    _inherit = "fix.ewaste.batch"

    recovery_ids = fields.One2many("fix.ewaste.material.recovery", "batch_id", string="Recovery")
    open_exception_count = fields.Integer(compute="_compute_open_exceptions")

    def _compute_open_exceptions(self):
        for rec in self:
            rec.open_exception_count = len(rec.exception_ids.filtered(lambda e: e.state == "open"))

    def _check_dispatch(self):
        """FR-ESG-024: the recycler must have a current, verified onward
        destination for this material at the moment of transfer."""
        super()._check_dispatch()
        partner = self.partner_id.sudo()
        current = partner.downstream_ids.filtered(
            lambda d: d.material_class in (self.material_type, "all")
        )._fix_current(c.today(self.env))
        if not current:
            raise UserError(
                "Recycler %s has no verified downstream destination for %s within the last "
                "%d days: verify where this material goes next before it leaves (BRU-ESG-18)."
                % (
                    partner.name,
                    dict(MATERIALS).get(self.material_type, self.material_type),
                    c.param_int(self.env, P_DOWNSTREAM_DAYS, DEFAULT_DOWNSTREAM_DAYS),
                )
            )


# ============================================================ p5 exceptions
class FixEwasteCertificateException(models.Model):
    """An item of a transferred batch that no returned certificate covers
    (T-03 / BRU-ESG-04). Raised by the certificate itself; resolved when a
    later certificate covers the item, or closed by a compliance officer -
    not the one who issued the certificate - on a documented finding. It
    never closes silently (AC-07)."""

    _name = "fix.ewaste.certificate.exception"
    _description = "E-Waste Certificate Exception"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "state, id desc"

    name = fields.Char(required=True, default="New", readonly=True)
    company_id = fields.Many2one("res.company", required=True, index=True, readonly=True)
    batch_id = fields.Many2one("fix.ewaste.batch", required=True, readonly=True, index=True)
    partner_id = fields.Many2one(related="batch_id.partner_id", store=True, string="Recycler")
    collection_id = fields.Many2one(
        "fix.ewaste.collection", string="Uncovered Item", required=True, readonly=True, index=True
    )
    certificate_id = fields.Many2one(
        "fix.ewaste.certificate", string="Raised by Certificate", readonly=True
    )
    kind = fields.Selection(
        [("uncovered", "Not on the Recycler's Certificate"), ("revoked", "Certificate Revoked")],
        required=True,
        default="uncovered",
        readonly=True,
    )
    raised_on = fields.Date(readonly=True)
    state = fields.Selection(
        [
            ("open", "Open"),
            ("resolved", "Resolved by Certificate"),
            ("closed", "Closed on Finding"),
        ],
        required=True,
        default="open",
    )
    resolved_certificate_id = fields.Many2one(
        "fix.ewaste.certificate", string="Resolved by", readonly=True
    )
    finding = fields.Text(string="Investigation Finding")
    closed_by_id = fields.Many2one("res.users", readonly=True)
    closed_on = fields.Date(readonly=True)

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | {
            "state",
            "resolved_certificate_id",
            "closed_by_id",
            "closed_on",
            "company_id",
            "batch_id",
            "collection_id",
            "certificate_id",
            "kind",
            "raised_on",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if not self or any(r.state != "open" for r in self):
            locked.add("finding")
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            raise UserError(
                "A certificate exception is raised by the certificate that leaves an item "
                "uncovered, never typed in."
            )
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = _seq(self.env, "fix.ewaste.certificate.exception", "EEXC/New")
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open() and "finding" in vals:
            for rec in self:
                if rec.state != "open" and c.changed_fields(rec, vals, {"finding"}):
                    c.frozen_refuse(rec, {"finding"}, "is %s" % rec.state)
        return super().write(vals)

    @api.model
    def _fix_raise(self, items, certificate, kind="uncovered"):
        out = self.browse()
        for item in items:
            if self.sudo().search_count([("collection_id", "=", item.id), ("state", "=", "open")]):
                continue
            exc = (
                self.sudo()
                ._guarded()
                .create(
                    {
                        "company_id": item.company_id.id,
                        "batch_id": certificate.batch_id.id,
                        "collection_id": item.id,
                        "certificate_id": certificate.id,
                        "kind": kind,
                        "raised_on": c.today(self.env),
                    }
                )
            )
            out |= exc
            c.notify(
                exc,
                "Uncovered e-waste item",
                "%s (batch %s, recycler %s) is not covered by certificate %s: obtain a "
                "certificate for it or investigate (BRU-ESG-04)."
                % (
                    item.name,
                    certificate.batch_id.name,
                    certificate.partner_id.name,
                    certificate.name,
                ),
                c.G_COMPLIANCE,
            )
        return self.browse(out.ids)

    @api.model
    def _fix_resolve(self, items, certificate):
        open_ = self.sudo().search([("collection_id", "in", items.ids), ("state", "=", "open")])
        if open_:
            open_._guarded().write({"state": "resolved", "resolved_certificate_id": certificate.id})
        return open_

    def action_close(self, finding=None):
        c.require_group(
            self.env, c.G_COMPLIANCE, "E-Waste Compliance Officer", "close a certificate exception"
        )
        if finding and str(finding).strip():
            self.write({"finding": str(finding).strip()})
        for rec in self:
            if rec.state != "open":
                raise UserError("%s is %s." % (rec.name, rec.state))
            if not (rec.finding or "").strip():
                raise UserError("Record the investigation finding for %s first." % rec.name)
            issuer = rec.sudo().certificate_id.issued_by_id
            if not self.env.su and issuer == self.env.user:
                raise UserError(
                    "You issued certificate %s: another compliance officer closes its "
                    "exception." % rec.certificate_id.name
                )
            rec._guarded().write(
                {"state": "closed", "closed_by_id": self.env.uid, "closed_on": c.today(rec.env)}
            )
        return True


# ============================================================ p5 recovery
class FixEwasteMaterialRecovery(models.Model):
    """What a processed batch yielded, by material class, weight and agreed
    rate (FR-ESG-014). Income is always the batch's (BRU-ESG-19): it is
    raised as the batch's recovery-income settlement, which the finance
    approver - never the person who recorded the weights - approves."""

    _name = "fix.ewaste.material.recovery"
    _description = "E-Waste Material Recovery"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(required=True, default="New", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company",
        required=True,
        index=True,
        readonly=True,
        default=lambda self: self.env.company,
        help="Set from the batch on create.",
    )
    batch_id = fields.Many2one(
        "fix.ewaste.batch", string="Processed Batch", required=True, ondelete="restrict", index=True
    )
    partner_id = fields.Many2one(related="batch_id.partner_id", store=True, string="Recycler")
    material_class = fields.Selection(RECOVERY_CLASSES, required=True)
    weight_kg = fields.Float(string="Recovered (kg)", required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    agreed_rate = fields.Monetary(string="Agreed Rate (per kg)", currency_field="currency_id")
    income_amount = fields.Monetary(
        string="Income", currency_field="currency_id", compute="_compute_income", store=True
    )
    recorded_on = fields.Date(readonly=True)
    settlement_id = fields.Many2one(
        "fix.ewaste.settlement", string="Income Settlement", readonly=True
    )
    state = fields.Selection(
        [("draft", "Draft"), ("raised", "Income Raised")], required=True, default="draft"
    )
    notes = fields.Text()

    _one_per_class = models.Constraint(
        "UNIQUE (batch_id, material_class)", "One recovery line per material class and batch"
    )
    _weight_positive = models.Constraint("CHECK (weight_kg > 0)", "A recovered weight is positive")
    _rate_positive = models.Constraint(
        "CHECK (agreed_rate IS NULL OR agreed_rate >= 0)", "A rate cannot be negative"
    )

    _TERMS = frozenset({"batch_id", "material_class", "weight_kg", "agreed_rate", "currency_id"})

    def _fix_guarded_fields(self) -> set:
        # company_id is read-only and set by create() from the batch
        return set(super()._fix_guarded_fields()) | {"state", "settlement_id", "recorded_on"}

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(r.state != "draft" for r in self):
            locked |= self._TERMS
        return locked

    @api.depends("weight_kg", "agreed_rate")
    def _compute_income(self):
        for rec in self:
            rec.income_amount = round((rec.weight_kg or 0.0) * (rec.agreed_rate or 0.0), 2)

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            c.require_group(
                self.env, c.G_DISPATCH, "E-Waste Dispatcher", "record material recovery"
            )
        for vals in vals_list:
            batch = self.env["fix.ewaste.batch"].sudo().browse(vals.get("batch_id"))
            if not batch.exists() or batch.state != "processed":
                raise UserError("Material recovery is recorded for a processed batch.")
            vals["company_id"] = batch.company_id.id
            if self.sudo().search_count(
                [("batch_id", "=", batch.id), ("material_class", "=", vals.get("material_class"))]
            ):
                raise UserError(
                    "Batch %s already has a %s recovery line: correct that line instead."
                    % (batch.name, dict(RECOVERY_CLASSES).get(vals.get("material_class"), "-"))
                )
            if vals.get("name", "New") == "New":
                vals["name"] = _seq(self.env, "fix.ewaste.material.recovery", "EREC/New")
        recs = super().create(vals_list)
        recs._guarded().write({"recorded_on": c.today(self.env)})
        recs._check_mass_balance()
        return self.browse(recs.ids)

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                if rec.state != "draft":
                    changed = c.changed_fields(rec, vals, self._TERMS)
                    if changed:
                        c.frozen_refuse(rec, changed, "is %s" % rec.state)
        res = super().write(vals)
        if {"weight_kg", "batch_id"} & set(vals):
            self._check_mass_balance()
        return res

    def _check_mass_balance(self):
        """Nothing is recovered beyond what the recycler processed (T-05)."""
        tol = c.param_float(self.env, c.P_TOLERANCE, c.DEFAULT_TOLERANCE)
        for batch in self.mapped("batch_id"):
            batch = batch.sudo()
            total = sum(batch.recovery_ids.mapped("weight_kg"))
            ceiling = batch.processed_weight_kg * (1 + tol / 100.0)
            if total > ceiling + 1e-6:
                raise ValidationError(
                    "Batch %s processed %.3f kg; the recovery lines total %.3f kg."
                    % (batch.name, batch.processed_weight_kg, total)
                )

    def action_raise_income(self):
        """Raise the batch's recovery income for the finance approver."""
        c.require_group(self.env, c.G_DISPATCH, "E-Waste Dispatcher", "raise recovery income")
        Settlement = self.env["fix.ewaste.settlement"]
        for batch in self.mapped("batch_id"):
            lines = self.filtered(lambda r, b=batch: r.batch_id == b)
            if any(r.state != "draft" for r in lines):
                raise UserError("Some of these recovery lines are already raised.")
            amount = round(sum(lines.mapped("income_amount")), 2)
            if amount <= 0:
                raise UserError("Batch %s: enter the agreed rate of each line first." % batch.name)
            contact = batch.sudo().partner_id.partner_id
            if not contact:
                raise UserError(
                    "Recycler %s has no business contact to invoice: link one on the recycler."
                    % batch.partner_id.name
                )
            weight = sum(lines.mapped("weight_kg"))
            live = Settlement.sudo().search(
                [
                    ("kind", "=", "recovery_income"),
                    ("batch_id", "=", batch.id),
                    ("state", "!=", "cancelled"),
                ],
                limit=1,
            )
            if live:
                # M18-05: one live income settlement per batch
                raise UserError(
                    "Batch %s already has recovery income %s: cancel it to raise the batch's "
                    "income again." % (batch.name, live.name)
                )
            # M18-05: the income is raised here only (trusted create), its
            # amount the lines' total; a typed recovery_income is refused
            settlement = Settlement._guarded().create(
                {
                    "kind": "recovery_income",
                    "batch_id": batch.id,
                    "partner_id": contact.id,
                    "company_id": batch.company_id.id,
                    "amount": amount,
                    "rate_per_kg": round(amount / weight, 2) if weight else 0.0,
                    "notes": "Material recovery: "
                    + ", ".join(
                        "%s %.3f kg" % (dict(RECOVERY_CLASSES)[r.material_class], r.weight_kg)
                        for r in lines
                    ),
                }
            )
            lines._guarded().write({"state": "raised", "settlement_id": settlement.id})
        return True


class FixEwasteSettlementCapture(models.Model):
    _inherit = "fix.ewaste.settlement"

    recovery_ids = fields.One2many(
        "fix.ewaste.material.recovery", "settlement_id", string="Recovery Lines"
    )

    def action_approve_settlement(self):
        """Spec §13 SoD: who recorded the recovery does not approve its income."""
        for rec in self:
            recorders = rec.sudo().recovery_ids.mapped("create_uid")
            if not self.env.su and self.env.user in recorders:
                raise UserError(
                    "You recorded the material recovery behind %s: another finance approver "
                    "approves its income." % rec.name
                )
        return super().action_approve_settlement()


# ============================================================ p9 factors
class FixEsgFactorSet(models.Model):
    """A versioned emissions-factor set (FR-ESG-019 / T-08, Q-09): proposed by
    one compliance officer with its source, activated by another; the active
    set's version is stamped on every figure computed with it (BRU-ESG-12).
    The factor is an input, not a published figure: the figures stay
    computed (BRU-ESG-11)."""

    _name = "fix.esg.factor.set"
    _description = "ESG Emissions Factor Set"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "company_id, id desc"

    name = fields.Char(string="Version", required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    co2_avoided_per_kg = fields.Float(
        string="CO2e Avoided per kg Recycled", required=True, digits=(12, 4)
    )
    source = fields.Char(string="Factor Source", help="e.g. US EPA WARM v16, DEFRA 2026")
    method_note = fields.Text(string="Method")
    evidence_attachment_id = fields.Many2one(
        "ir.attachment", string="Source Document", ondelete="restrict"
    )
    evidence_file = fields.Binary(string="Upload Source Document", store=False)
    evidence_filename = fields.Char(string="Source File Name", store=False)
    state = fields.Selection(
        [("draft", "Proposed"), ("active", "Active"), ("retired", "Retired")],
        required=True,
        default="draft",
    )
    activated_by_id = fields.Many2one("res.users", readonly=True)
    activated_on = fields.Date(readonly=True)
    retired_on = fields.Date(readonly=True)

    _version_once = models.Constraint(
        "UNIQUE (company_id, name)", "Each factor-set version is used once"
    )
    _factor_positive = models.Constraint(
        "CHECK (co2_avoided_per_kg > 0)", "An emissions factor is positive"
    )

    _TERMS = frozenset(
        {
            "name",
            "company_id",
            "co2_avoided_per_kg",
            "source",
            "method_note",
            "evidence_attachment_id",
        }
    )
    _UPLOADS = {"evidence_attachment_id": ("evidence_file", "evidence_filename")}

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | {
            "state",
            "activated_by_id",
            "activated_on",
            "retired_on",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(r.state != "draft" for r in self):
            locked |= self._TERMS
        return c.lock_uploads(locked, self._UPLOADS)

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            c.require_group(
                self.env, c.G_COMPLIANCE, "E-Waste Compliance Officer", "propose a factor set"
            )
        staged = c.stage_uploads(vals_list, self._UPLOADS)
        recs = super().create(vals_list)
        c.attach_staged(recs, staged)
        return recs

    def write(self, vals):
        vals = c.lift_uploads(self, vals, self._UPLOADS)
        if self and not self._fix_guard_open():
            for rec in self:
                if rec.state != "draft":
                    changed = c.changed_fields(rec, vals, self._TERMS)
                    if changed:
                        c.frozen_refuse(rec, changed, "is %s (propose a new version)" % rec.state)
        return super().write(vals)

    @api.model
    def _fix_active_for(self, company):
        return self.sudo().search(
            [("company_id", "=", company.id), ("state", "=", "active")], limit=1
        )

    def action_activate(self):
        c.require_group(
            self.env, c.G_COMPLIANCE, "E-Waste Compliance Officer", "activate a factor set"
        )
        today = c.today(self.env)
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is not proposed." % rec.name)
            if not self.env.su and rec.create_uid == self.env.user:
                raise UserError(
                    "You proposed %s: another compliance officer activates it." % rec.name
                )
            if not (rec.source or "").strip() or not rec.evidence_attachment_id:
                raise UserError("%s needs its source and the source document." % rec.name)
            previous = self.sudo().search(
                [("company_id", "=", rec.company_id.id), ("state", "=", "active")]
            )
            previous._guarded().write({"state": "retired", "retired_on": today})
            rec._guarded().write(
                {"state": "active", "activated_by_id": self.env.uid, "activated_on": today}
            )
            rec.message_post(
                body="Active from %s; figures computed from now on carry version %s."
                % (today, rec.name)
            )
        return True


# ============================================================ p10 register
class FixEwasteObligation(models.Model):
    """The e-waste subset of the regulatory register (FR-ESG-016; M60 owns
    the enterprise register): each instrument's obligation on the company,
    its owner, evidence source and review clock. Reviewed at least
    quarterly (BRU-ESG-16); an overdue review is flagged daily (AUT-ESG-19)."""

    _name = "fix.ewaste.obligation"
    _description = "E-Waste Regulatory Obligation"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "next_review, id"

    name = fields.Char(string="Obligation", required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    instrument = fields.Selection(
        [
            ("ewaste_rules_2021", "Hazardous Waste (E-waste) Management Rules 2021"),
            ("eca_1995", "Environment Conservation Act 1995"),
            ("ecr", "Environment Conservation Rules"),
            ("btrc_weee_2022", "BTRC WEEE Guidelines 2022"),
            ("basel", "Basel Convention (e-waste amendments)"),
            ("other", "Other"),
        ],
        required=True,
        default="ewaste_rules_2021",
    )
    citation = fields.Char(string="Clause / Section", required=True)
    obligation_text = fields.Text(string="What the Company Must Do", required=True)
    applies_because = fields.Text()
    owner_id = fields.Many2one("res.users", string="Owner")
    evidence_source = fields.Char(string="Evidence Source")
    frequency = fields.Selection(
        [
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("annual", "Annual"),
            ("event", "On Event"),
        ],
        string="Obligation Frequency",
        required=True,
        default="quarterly",
    )
    next_review = fields.Date()
    last_reviewed = fields.Date(readonly=True)
    last_reviewed_by_id = fields.Many2one("res.users", readonly=True)
    last_review_note = fields.Text(readonly=True)
    compliance_status = fields.Selection(
        [
            ("unassessed", "Not Yet Assessed"),
            ("compliant", "Compliant"),
            ("partial", "Partially Compliant"),
            ("non_compliant", "Non-Compliant"),
            ("not_applicable", "Not Applicable"),
        ],
        required=True,
        default="unassessed",
        tracking=True,
    )
    review_status = fields.Selection(
        [
            ("compliant", "Compliant"),
            ("partial", "Partially Compliant"),
            ("non_compliant", "Non-Compliant"),
            ("not_applicable", "Not Applicable"),
        ],
        string="Review Finding",
    )
    review_note = fields.Text(string="Review Note")
    review_overdue = fields.Boolean(compute="_compute_overdue")
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("retired", "Retired")],
        required=True,
        default="draft",
    )

    _TERMS = frozenset({"instrument", "citation", "obligation_text", "company_id"})

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | {
            "state",
            "compliance_status",
            "last_reviewed",
            "last_reviewed_by_id",
            "last_review_note",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(r.state != "draft" for r in self):
            locked |= self._TERMS
        if not self or any(r.state != "active" for r in self):
            locked |= {"review_status", "review_note"}
        return locked

    def _compute_overdue(self):
        today = c.today(self.env)
        for rec in self:
            rec.review_overdue = bool(
                rec.state == "active" and rec.next_review and rec.next_review < today
            )

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            c.require_group(
                self.env, c.G_COMPLIANCE, "E-Waste Compliance Officer", "record an obligation"
            )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                names = set(self._TERMS) if rec.state != "draft" else set()
                if rec.state != "active":
                    names |= {"review_status", "review_note"}
                changed = c.changed_fields(rec, vals, names)
                if changed:
                    c.frozen_refuse(rec, changed, "is %s" % rec.state)
        return super().write(vals)

    def _fix_next(self, start):
        days = min(REVIEW_DAYS.get(self.frequency, MAX_REVIEW_DAYS), MAX_REVIEW_DAYS)
        return start + timedelta(days=days)

    def action_activate(self):
        c.require_group(
            self.env, c.G_COMPLIANCE, "E-Waste Compliance Officer", "activate an obligation"
        )
        today = c.today(self.env)
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is not a draft." % rec.name)
            if not rec.owner_id or not (rec.evidence_source or "").strip():
                raise UserError("%s needs its owner and its evidence source." % rec.name)
            vals = {"state": "active"}
            if not rec.next_review or rec.next_review > rec._fix_next(today):
                vals["next_review"] = rec._fix_next(today)
            rec._guarded().write(vals)
        return True

    def action_review(self, review_status=None, review_note=None):
        """Record the review's finding; the next review is at most a quarter
        away (BRU-ESG-16)."""
        c.require_group(
            self.env, c.G_COMPLIANCE, "E-Waste Compliance Officer", "review an obligation"
        )
        inputs = {}
        if review_status:
            inputs["review_status"] = review_status
        if review_note and str(review_note).strip():
            inputs["review_note"] = str(review_note).strip()
        if inputs:
            self.write(inputs)
        today = c.today(self.env)
        for rec in self:
            if rec.state != "active":
                raise UserError("%s is not active." % rec.name)
            if not rec.review_status or not (rec.review_note or "").strip():
                raise UserError("Enter the review finding and note for %s first." % rec.name)
            rec._guarded().write(
                {
                    "compliance_status": rec.review_status,
                    "last_reviewed": today,
                    "last_reviewed_by_id": self.env.uid,
                    "last_review_note": rec.review_note,
                    "next_review": rec._fix_next(today),
                    "review_status": False,
                    "review_note": False,
                }
            )
            rec.message_post(
                body="Reviewed by %s: %s. %s"
                % (
                    self.env.user.name,
                    dict(self._fields["compliance_status"].selection)[rec.compliance_status],
                    rec.last_review_note,
                )
            )
        return True

    def action_retire(self):
        c.require_group(
            self.env, c.G_COMPLIANCE, "E-Waste Compliance Officer", "retire an obligation"
        )
        for rec in self:
            rec._guarded().write({"state": "retired"})
        return True

    @api.model
    def cron_review_due(self):
        """AUT-ESG-19: flag every active obligation past its review date."""
        today = c.today(self.env)
        due = self.sudo().search([("state", "=", "active"), ("next_review", "<", today)])
        for rec in due:
            c.notify(
                rec,
                "Regulatory review overdue",
                "%s (%s) was due for review on %s (BRU-ESG-16)."
                % (rec.name, rec.citation, rec.next_review),
                c.G_COMPLIANCE,
            )
        return len(due)
