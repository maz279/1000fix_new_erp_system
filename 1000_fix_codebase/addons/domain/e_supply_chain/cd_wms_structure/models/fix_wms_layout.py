# fix_wms_layout — M41 capture pass 2 (2026-11-19): the structure the spec's
# §10.1 names and the Physical Structure page could not capture.
#
#   * FR-WMS-003 / BRU-WMS-02: warehouse execution is OPT-IN per location. A
#     warehouse that is not enabled runs on M15 alone, so it has no zones and
#     no bins; enabling is a Warehouse Supervisor's (or the IT
#     administrator's) decision. Its wave cut-offs and shift pattern are the
#     warehouse's own configuration (§10.1 fix.wh.warehouse).
#   * FR-WMS-001 / T-02: zones are typed bulk / pick / inspection / quarantine /
#     staging / returns / secure, and a zone may be reserved for one ownership
#     class: its bins then hold nothing else.
#   * FR-WMS-002 / T-09: a bin carries its (aisle, bay, level, position)
#     coordinate, the pick-face flag, its dimensions and its weight and volume
#     limits. The serpentine pick sequence is computed from the coordinate.
import re

from odoo import api, fields, models
from odoo.exceptions import AccessError, ValidationError

SUPERVISOR = "cd_wms_structure.group_warehouse_supervisor"
_CUTOFF = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")

OWNERSHIP = [
    ("any", "Any Class"),
    ("owned", "Owned Stock"),
    ("consignment", "Supplier Consignment"),
    ("customer", "Customer Property"),
    ("bench", "Bench / WIP"),
    ("warranty", "Warranty Reserve"),
]


def may_configure(env) -> bool:
    """A Warehouse Supervisor or the IT administrator (spec section 13, R33)."""
    return env.su or env.user.has_group(SUPERVISOR) or env.user.has_group("base.group_system")


class FixWarehouseWms(models.Model):
    _inherit = "fix.warehouse"

    wms_enabled = fields.Boolean(
        string="Warehouse Execution Enabled",
        default=False,
        tracking=True,
        help="FR-WMS-003 / BRU-WMS-02: only an enabled warehouse is laid out in zones and "
        "bins and runs put-away, waves and RF tasks. A standard branch stockroom stays on "
        "the M15 ledger alone.",
    )
    wave_cutoffs = fields.Char(
        string="Wave Cut-offs (HH:MM, comma separated)",
        help="The times scheduled waves close, e.g. 10:00, 15:30.",
    )
    shift_pattern = fields.Selection(
        [
            ("one", "One shift (06-14)"),
            ("two", "Two shifts (06-22)"),
            ("three", "Three shifts (24 h)"),
        ],
        string="Shift Pattern",
        default="one",
    )

    @api.constrains("wave_cutoffs")
    def _check_cutoffs(self):
        for rec in self:
            for part in (rec.wave_cutoffs or "").split(","):
                part = part.strip()
                if part and not _CUTOFF.match(part):
                    raise ValidationError("Wave cut-off %r is not a time (HH:MM, 24-hour)." % part)

    @api.model_create_multi
    def create(self, vals_list):
        if any(vals.get("wms_enabled") for vals in vals_list) and not may_configure(self.env):
            raise AccessError(
                "Only a Warehouse Supervisor or the IT administrator enables warehouse "
                "execution (BRU-WMS-02)."
            )
        return super().create(vals_list)

    def write(self, vals):
        if (
            "wms_enabled" in vals
            and not may_configure(self.env)
            and any(bool(vals["wms_enabled"]) != rec.wms_enabled for rec in self)
        ):
            raise AccessError(
                "Only a Warehouse Supervisor or the IT administrator enables or disables "
                "warehouse execution (BRU-WMS-02)."
            )
        return super().write(vals)


class FixWarehouseZoneWms(models.Model):
    _inherit = "fix.warehouse.zone"

    zone_type = fields.Selection(
        selection_add=[
            ("bulk", "Bulk Storage"),
            ("pick", "Pick Face"),
            ("staging", "Staging"),
            ("secure", "Secure Cage"),
        ],
        ondelete={
            "bulk": "set default",
            "pick": "set default",
            "staging": "set default",
            "secure": "set default",
        },
    )
    ownership_class = fields.Selection(
        OWNERSHIP,
        string="Reserved for Ownership Class",
        required=True,
        default="any",
        help="T-02: a zone reserved for one class (brand consignment kept apart) holds only "
        "bins of that class.",
    )
    sequence = fields.Integer(
        string="Walk Sequence",
        default=10,
        help="FR-WMS-022: the order zones are walked in a pick path.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        Warehouse = self.env["fix.warehouse"].sudo()
        for vals in vals_list:
            warehouse = Warehouse.browse(vals.get("warehouse_id") or 0).exists()
            if warehouse and not warehouse.wms_enabled:
                raise ValidationError(
                    "Warehouse %s does not run warehouse execution: a supervisor enables it "
                    "first. A warehouse that is not enabled runs on the M15 ledger alone, "
                    "with no zones or bins (FR-WMS-003, BRU-WMS-02)." % warehouse.name
                )
        return super().create(vals_list)

    @api.constrains("ownership_class")
    def _check_bin_classes(self):
        for zone in self:
            if zone.ownership_class == "any":
                continue
            stray = zone.bin_ids.filtered(
                lambda b, cls=zone.ownership_class: b.ownership_class != cls
            )
            if stray:
                raise ValidationError(
                    "Zone %s is reserved for %s stock: bin %s is %s (T-02)."
                    % (zone.name, zone.ownership_class, stray[0].name, stray[0].ownership_class)
                )


class FixWarehouseBinWms(models.Model):
    _inherit = "fix.warehouse.bin"
    _order = "pick_sequence, id"

    aisle = fields.Char(string="Aisle", help="T-09: the aisle code, e.g. A.")
    bay = fields.Integer(string="Bay / Rack", default=0)
    level = fields.Integer(string="Level", default=0)
    position = fields.Integer(string="Position", default=0)
    is_pick_face = fields.Boolean(
        string="Pick Face",
        help="FR-WMS-002: a pick-face bin is replenished from bulk and is where the "
        "near-pick-face put-away strategy aims.",
    )
    length_cm = fields.Float(string="Length (cm)")
    width_cm = fields.Float(string="Width (cm)")
    height_cm = fields.Float(string="Height (cm)")
    max_weight_kg = fields.Float(string="Weight Limit (kg)", help="0 = no weight limit.")
    max_volume_m3 = fields.Float(
        string="Volume Limit (m³)",
        digits=(12, 4),
        help="0 = the bin's own inner dimensions, or no limit when they are not given.",
    )
    pick_sequence = fields.Integer(
        string="Pick Sequence",
        compute="_compute_pick_sequence",
        store=True,
        index=True,
        help="T-09 / FR-WMS-022: zone walk order, then aisle, then the bay in a serpentine "
        "(odd aisles walked up, even aisles back down), then level and position.",
    )

    @api.constrains(
        "bay",
        "level",
        "position",
        "length_cm",
        "width_cm",
        "height_cm",
        "max_weight_kg",
        "max_volume_m3",
    )
    def _check_dimensions(self):
        for rec in self:
            values = (
                rec.bay,
                rec.level,
                rec.position,
                rec.length_cm,
                rec.width_cm,
                rec.height_cm,
                rec.max_weight_kg,
                rec.max_volume_m3,
            )
            if any((v or 0) < 0 for v in values):
                raise ValidationError(
                    "Bin %s: a coordinate, dimension or limit cannot be negative." % rec.name
                )

    @api.constrains("ownership_class", "zone_id")
    def _check_zone_class(self):
        for rec in self:
            zone_class = rec.zone_id.ownership_class or "any"
            if zone_class != "any" and rec.ownership_class != zone_class:
                raise ValidationError(
                    "Bin %s is in zone %s, which is reserved for %s stock (T-02)."
                    % (rec.name, rec.zone_id.name, zone_class)
                )

    def _fix_volume_limit(self) -> float:
        """m³ the bin holds: its limit, else its inner dimensions, else 0 (none)."""
        self.ensure_one()
        if self.max_volume_m3:
            return self.max_volume_m3
        if self.length_cm and self.width_cm and self.height_cm:
            return round(self.length_cm * self.width_cm * self.height_cm / 1_000_000.0, 6)
        return 0.0

    @staticmethod
    def _aisle_rank(aisle) -> int:
        aisle = (aisle or "").strip().upper()
        if not aisle:
            return 0
        if aisle.isdigit():
            return int(aisle)
        rank = 0
        for ch in aisle:
            rank = rank * 27 + (ord(ch) - 64 if "A" <= ch <= "Z" else 0)
        return rank

    @api.depends("zone_id.sequence", "aisle", "bay", "level", "position")
    def _compute_pick_sequence(self):
        for rec in self:
            aisle = min(self._aisle_rank(rec.aisle), 9999)
            bay = min(rec.bay or 0, 999)
            # serpentine: every second aisle is walked back down
            bay_walk = bay if aisle % 2 else 999 - bay
            rec.pick_sequence = (
                min(rec.zone_id.sequence or 0, 99) * 10_000_000
                + aisle * 100_000
                + bay_walk * 100
                + min(rec.level or 0, 9) * 10
                + min(rec.position or 0, 9)
            )
