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
from odoo.exceptions import UserError, ValidationError

from .fix_cash_shift import fill_operating_unit

# an intake whose device is physically at the counter
CUSTODY_STATES = ("in_progress", "handover_pending")
# A02 pass 2 (M04-05): a service order holds its location until the device
# leaves the branch for good
ORDER_RELEASED_STATES = ("delivered", "closed", "cancelled")
# an on-site job's device never comes to the branch
ORDER_NO_SHELF_TYPES = ("onsite",)


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
    order_ids = fields.One2many("fix.service.order", "storage_location_id", string="Service Orders")
    occupied_by_id = fields.Many2one(
        "fix.walkin.intake",
        string="Holds Device Of",
        compute="_compute_occupancy",
        store=True,
    )
    occupied_by_order_id = fields.Many2one(
        "fix.service.order",
        string="Holds Order",
        compute="_compute_occupancy",
        store=True,
    )
    occupied = fields.Boolean(compute="_compute_occupancy", store=True, string="Occupied")

    @api.depends("branch_id", "code", "zone")
    def _compute_name(self):
        for rec in self:
            rec.name = "%s %s" % (rec.branch_id.code or rec.branch_id.name or "", rec.code or "")

    @api.depends(
        "intake_ids.state",
        "intake_ids.storage_location_id",
        "order_ids.state",
        "order_ids.storage_location_id",
    )
    def _compute_occupancy(self):
        for rec in self:
            held = rec.intake_ids.filtered(lambda i: i.state in CUSTODY_STATES)[:1]
            order = rec.order_ids.filtered(lambda o: o.state not in ORDER_RELEASED_STATES)[:1]
            rec.occupied_by_id = held
            rec.occupied_by_order_id = order
            rec.occupied = bool(held or order)

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


class FixWalkinStorageHandover(models.Model):
    """M04-05: at the hand-off the intake's shelf passes to its service order."""

    _inherit = "fix.walkin.intake"

    @api.constrains("storage_location_id", "state")
    def _check_storage_not_held_by_order(self):
        """BRU-FRD-06: a shelf a service order holds takes no intake's device."""
        Order = self.env["fix.service.order"].sudo()
        for rec in self.filtered(lambda r: r.storage_location_id and r.state in CUSTODY_STATES):
            held = Order.search(
                [
                    ("storage_location_id", "=", rec.storage_location_id.id),
                    ("state", "not in", ORDER_RELEASED_STATES),
                    ("id", "!=", rec.service_order_id.id or 0),
                ],
                limit=1,
            )
            if held:
                raise ValidationError(
                    "Location %s already holds the device of %s (BRU-FRD-06)."
                    % (rec.storage_location_id.name, held.name)
                )

    def action_complete_handover(self):
        result = super().action_complete_handover()
        for rec in self.sudo():
            order = rec.service_order_id
            if rec.storage_location_id and order and not order.storage_location_id:
                order._guarded().write({"storage_location_id": rec.storage_location_id.id})
        return result


class FixServiceOrderStorage(models.Model):
    """A02 pass 2 (M04-05, FR-FRD-011 / BRU-FRD-06): where a device waiting at
    the branch is kept. A Ready device had no location at all: the counter
    searched the back office for it. The order takes its intake's shelf at
    the hand-off, is given one when it becomes Ready (required once the branch
    has registered its shelves), and frees it when the device is delivered or
    the order is cancelled. One device per location, one location per device."""

    _inherit = "fix.service.order"

    storage_location_id = fields.Many2one(
        "fix.storage.location",
        string="Storage Location",
        domain="[('branch_id', '=', branch_id)]",
        tracking=True,
        index=True,
        copy=False,
        help="The shelf or bin the device waits on at the branch (freed at delivery or "
        "cancellation).",
    )

    def _fd_holds_shelf(self) -> bool:
        self.ensure_one()
        return bool(self.storage_location_id) and self.state not in ORDER_RELEASED_STATES

    @api.constrains("storage_location_id", "state", "device_id", "branch_id")
    def _check_order_storage_location(self):
        """BRU-FRD-06: a location holds one device, a device one location."""
        Intake = self.env["fix.walkin.intake"].sudo()
        for order in self.filtered(lambda o: o._fd_holds_shelf()):
            loc = order.storage_location_id
            if loc.branch_id != order.branch_id:
                raise ValidationError(
                    "Location %s is at %s, not at the order's branch %s."
                    % (loc.name, loc.branch_id.display_name, order.branch_id.display_name)
                )
            other = self.sudo().search(
                [
                    ("id", "!=", order.id),
                    ("storage_location_id", "=", loc.id),
                    ("state", "not in", ORDER_RELEASED_STATES),
                ],
                limit=1,
            )
            intake = Intake.search(
                [("storage_location_id", "=", loc.id), ("state", "in", CUSTODY_STATES)], limit=1
            )
            if other or intake:
                raise ValidationError(
                    "Location %s already holds a device (%s). A location holds one device at a "
                    "time (BRU-FRD-06)."
                    % (loc.name, other.name if other else "intake of %s" % intake.customer_id.name)
                )
            if order.device_id:
                twin = self.sudo().search(
                    [
                        ("id", "!=", order.id),
                        ("device_id", "=", order.device_id.id),
                        ("storage_location_id", "!=", False),
                        ("state", "not in", ORDER_RELEASED_STATES),
                    ],
                    limit=1,
                )
                if twin:
                    raise ValidationError(
                        "Device %s is already stored at %s for %s (a device is in one location)."
                        % (order.device_id.display_name, twin.storage_location_id.name, twin.name)
                    )

    def _fd_branch_has_shelves(self) -> bool:
        self.ensure_one()
        return bool(
            self.branch_id
            and self.env["fix.storage.location"]
            .sudo()
            .search_count([("branch_id", "=", self.branch_id.id), ("active", "=", True)], limit=1)
        )

    def action_ready(self):
        """M04-05: a device Ready for collection at a branch that registered
        its shelves is put on one first."""
        for order in self:
            if (
                not order.storage_location_id
                and order.service_type not in ORDER_NO_SHELF_TYPES
                and order._fd_branch_has_shelves()
            ):
                raise UserError(
                    "Order %s: put the device on a storage location of %s before it is Ready "
                    "for collection, so the counter finds it (FR-FRD-011)."
                    % (order.name, order.branch_id.display_name)
                )
        return super().action_ready()
