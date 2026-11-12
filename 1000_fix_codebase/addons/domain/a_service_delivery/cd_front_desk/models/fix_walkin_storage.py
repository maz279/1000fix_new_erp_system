# Branch storage locations (FR-FRD-011, T-09, BRU-FRD-06).
#
# M04 build, 13 Nov 2026: the bin of a device in custody was free text
# (storage_bin_code). Two devices could be typed into one bin, one device
# could be in two intakes' bins, and nothing listed a branch's shelves, so
# "found in 60 seconds" had nothing to search. A branch now registers its
# locations; an intake in custody takes one of them; a location holds one
# device at a time and is free again once the intake leaves custody.
#
# Loaded after fix_walkin_intake (it extends fix.walkin.intake): keep the name.
from odoo import api, fields, models
from odoo.exceptions import ValidationError

from .fix_cash_shift import fill_operating_unit

# an intake whose device is physically at the counter
CUSTODY_STATES = ("in_progress", "handover_pending")


class FixStorageLocation(models.Model):
    """A shelf or bin at a branch that holds one customer device."""

    _name = "fix.storage.location"
    _description = "Branch Storage Location"
    _inherit = ["mail.thread"]
    _order = "branch_id, code"

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    branch_id = fields.Many2one("fix.branch", string="Branch", required=True, index=True)
    code = fields.Char(
        string="Location Code", required=True, help="As printed on the shelf label, e.g. B-03-2."
    )
    zone = fields.Char(string="Zone / Room")
    shelf = fields.Char()
    bin = fields.Char()
    secure = fields.Boolean(
        string="Secure Cabinet", help="Lockable storage for high-value devices."
    )
    active = fields.Boolean(default=True)
    intake_ids = fields.One2many("fix.walkin.intake", "storage_location_id", string="Intakes")
    occupied_by_id = fields.Many2one(
        "fix.walkin.intake",
        string="Holds Device Of",
        compute="_compute_occupancy",
        store=True,
    )
    occupied = fields.Boolean(compute="_compute_occupancy", store=True, string="Occupied")

    @api.depends("branch_id", "code", "zone")
    def _compute_name(self):
        for rec in self:
            rec.name = "%s %s" % (rec.branch_id.code or rec.branch_id.name or "", rec.code or "")

    @api.depends("intake_ids.state", "intake_ids.storage_location_id")
    def _compute_occupancy(self):
        for rec in self:
            held = rec.intake_ids.filtered(lambda i: i.state in CUSTODY_STATES)[:1]
            rec.occupied_by_id = held
            rec.occupied = bool(held)

    @api.constrains("branch_id", "code")
    def _check_unique_code(self):
        for rec in self:
            twin = self.with_context(active_test=False).search(
                [
                    ("id", "!=", rec.id),
                    ("branch_id", "=", rec.branch_id.id),
                    ("code", "=ilike", rec.code),
                ],
                limit=1,
            )
            if twin:
                raise ValidationError(
                    "%s already has a storage location %s." % (rec.branch_id.display_name, rec.code)
                )

    @api.model_create_multi
    def create(self, vals_list):
        fill_operating_unit(self.env, vals_list)
        return super().create(vals_list)


class FixWalkinStorage(models.Model):
    _inherit = "fix.walkin.intake"

    storage_location_id = fields.Many2one(
        "fix.storage.location",
        string="Storage Location",
        domain="[('branch_id', '=', branch_id), ('occupied', '=', False)]",
        tracking=True,
        index=True,
    )

    @api.onchange("storage_location_id")
    def _onchange_storage_location(self):
        if self.storage_location_id:
            self.storage_bin_code = self.storage_location_id.code

    def write(self, vals):
        if vals.get("storage_location_id") and "storage_bin_code" not in vals:
            loc = self.env["fix.storage.location"].browse(vals["storage_location_id"])
            vals = dict(vals, storage_bin_code=loc.code)
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        Loc = self.env["fix.storage.location"]
        for vals in vals_list:
            if vals.get("storage_location_id") and not vals.get("storage_bin_code"):
                vals["storage_bin_code"] = Loc.browse(vals["storage_location_id"]).code
        return super().create(vals_list)

    @api.constrains("storage_location_id", "state", "device_id", "branch_id")
    def _check_storage_location(self):
        """T-09 / BRU-FRD-06: one device per location, one location per device."""
        for rec in self.filtered(lambda r: r.storage_location_id and r.state in CUSTODY_STATES):
            loc = rec.storage_location_id
            if loc.branch_id != rec.branch_id:
                raise ValidationError(
                    "Location %s is at %s, not at the intake's branch %s."
                    % (loc.name, loc.branch_id.display_name, rec.branch_id.display_name)
                )
            other = self.sudo().search(
                [
                    ("id", "!=", rec.id),
                    ("storage_location_id", "=", loc.id),
                    ("state", "in", CUSTODY_STATES),
                ],
                limit=1,
            )
            if other:
                raise ValidationError(
                    "Location %s already holds a device (intake of %s). A location holds one "
                    "device at a time (BRU-FRD-06)." % (loc.name, other.customer_id.display_name)
                )
            if rec.device_id:
                twin = self.sudo().search(
                    [
                        ("id", "!=", rec.id),
                        ("device_id", "=", rec.device_id.id),
                        ("storage_location_id", "!=", False),
                        ("state", "in", CUSTODY_STATES),
                    ],
                    limit=1,
                )
                if twin:
                    raise ValidationError(
                        "Device %s is already stored at %s (T-09: a device is in one location)."
                        % (rec.device_id.display_name, twin.storage_location_id.name)
                    )
