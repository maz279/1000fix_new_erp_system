# fix_inventory_approval — the two-person rule and the shared stock helpers
# of M15/M41 (A06 audit 2026-11-03, remediation S1/S2/S9).
#
# The audit found no approval anywhere in M15/M41: a plain user posted a
# BDT 500,000 count write-down and a BDT 500,000 scrap, self-approved an RTV
# and re-classed consignment stock as owned. Every inventory approval now
# needs a second person:
#   1. the approver holds the CODED Inventory Controller group (never a
#      group read from the user-writable M63 rule book, A11 audit M63-2);
#   2. the approver is not the requester, the creator, nor anyone the model
#      adds (the counter, the quarantiner, the blocker);
#   3. the stamp (requested/approved by and at) is written from env.user
#      inside the action, through the guard, never from a parameter.
# Thresholds and tolerances are business decisions (report section 7): they
# are ir.config_parameter keys with a conservative default of 0, which means
# EVERY variance / write-off / transfer needs the approval.
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

CONTROLLER_GROUP = "cd_wms_structure.group_inventory_controller"
STOREKEEPER_GROUP = "cd_wms_structure.group_storekeeper"
OPERATOR_GROUP = "cd_wms_structure.group_warehouse_operator"

# ir.config_parameter keys (documented in the runbook) and their defaults.
PARAM_COUNT_TOLERANCE_PCT = "cd_inventory.count_variance_tolerance_pct"
PARAM_VAN_TOLERANCE_PCT = "cd_inventory.van_variance_tolerance_pct"
PARAM_WRITEOFF_THRESHOLD = "cd_inventory.writeoff_approval_threshold"
PARAM_TRANSFER_THRESHOLD = "cd_inventory.transfer_approval_threshold"

# Ownership classes that are 1000FiX's own inventory (BRU-INV-02): supplier
# consignment and customer property are held, never valued.
VALUED_CLASSES = ("owned", "van", "bench", "warranty")

# Units of measure counted in whole pieces.
WHOLE_UNITS = {"PCS", "PC", "EA", "NOS", "NO", "UNIT", "UNITS", "SET", "PAIR"}


def inv_param(env, key, default=0.0) -> float:
    """A numeric inventory parameter; an unreadable value falls back to the
    conservative default rather than to a permissive one."""
    raw = env["ir.config_parameter"].sudo().get_param(key, default)
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return float(default)
    return max(value, 0.0)


def is_whole_unit(part) -> bool:
    return (part.uom or "PCS").strip().upper() in WHOLE_UNITS


def check_quantity(part, qty, what="quantity", allow_zero=False):
    """Refuse negative, zero (unless allowed) and fractional-piece quantities."""
    qty = qty or 0.0
    if qty < 0 or (qty == 0 and not allow_zero):
        raise UserError(
            "The %s of %s must be %s (got %s)."
            % (what, part.part_number, "zero or more" if allow_zero else "positive", qty)
        )
    if is_whole_unit(part) and abs(qty - round(qty)) > 1e-9:
        raise UserError(
            "%s is counted in whole pieces (%s): a %s of %s is not possible."
            % (part.part_number, part.uom or "PCS", what, qty)
        )


def location_class(location, requested="owned") -> str:
    """The ownership class a movement at this location books into: company
    stock at a technician's van is the `van` class (that is where the van
    ledger lives), every other requested class is kept as asked."""
    if requested == "owned" and location.location_type == "van":
        return "van"
    return requested


def check_location_usable(location, user_env=None):
    """A movement may only touch an active location the acting user may see
    (company and operating unit, A06 audit M15-14)."""
    if not location.active or location.state != "active":
        raise UserError("Location %s is not active and cannot move stock." % location.code)
    env = user_env or location.env
    if env.su:
        return
    if location.company_id and location.company_id not in env.companies:
        raise AccessError("Location %s belongs to another company." % location.code)
    try:
        location.with_env(env).check_access("read")
    except AccessError as exc:
        raise AccessError(
            "You have no access to location %s (another operating unit)." % location.code
        ) from exc
    user = env.user
    ou = location.operating_unit_id
    # the same set the OCA record rules evaluate (OU managers see all)
    allowed = user.operating_units() if hasattr(user, "operating_units") else None
    if ou and allowed is not None and ou not in allowed:
        raise AccessError(
            "Location %s belongs to operating unit %s, which you are not assigned to."
            % (location.code, ou.display_name)
        )


class FixInventoryApprovalMixin(models.AbstractModel):
    """Requested-by / approved-by evidence and the Inventory Controller
    two-person rule."""

    _name = "fix.inventory.approval.mixin"
    _inherit = ["fix.guarded.mixin"]
    _description = "Inventory Two-Person Approval"

    requested_by_id = fields.Many2one("res.users", string="Requested By", readonly=True, copy=False)
    requested_at = fields.Datetime(string="Approval Requested On", readonly=True, copy=False)
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True, copy=False)
    approved_at = fields.Datetime(string="Approved On", readonly=True, copy=False)
    approval_note = fields.Char(string="Approval Note", copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "requested_by_id",
            "requested_at",
            "approved_by_id",
            "approved_at",
        }

    # ---- hooks -----------------------------------------------------------
    def _inv_excluded_users(self):
        """Who may never approve this record (segregation of duties)."""
        self.ensure_one()
        return self.create_uid | self.requested_by_id

    def _inv_approval_label(self) -> str:
        self.ensure_one()
        return "%s %s" % (self._description, getattr(self, "name", self.id))

    # ---- checks ----------------------------------------------------------
    def _inv_check_approver(self):
        """Refuse unless env.user is an Inventory Controller who is not
        excluded on any of these records. Trusted code (sudo) is exempt, as
        it is for the field guard."""
        if self.env.su:
            return
        user = self.env.user
        if not user.has_group(CONTROLLER_GROUP):
            raise AccessError(
                "Only an Inventory Controller can approve %s."
                % ", ".join(rec._inv_approval_label() for rec in self)
            )
        for rec in self:
            if user in rec._inv_excluded_users():
                raise UserError(
                    "Segregation of duties: you requested, raised or counted %s, so a "
                    "different Inventory Controller must approve it." % rec._inv_approval_label()
                )

    def _inv_stamp_request(self, user=None):
        """Stamp the request: the acting user, or (when an approver approves a
        draft directly) the person who raised it, never the approver."""
        for rec in self:
            requester = user if user is not None else self.env.user
            rec._guarded().write(
                {"requested_by_id": requester.id, "requested_at": fields.Datetime.now()}
            )

    def _inv_stamp_approval(self, note=None):
        vals = {"approved_by_id": self.env.user.id, "approved_at": fields.Datetime.now()}
        if note:
            vals["approval_note"] = note
        self._guarded().write(vals)

    def _inv_clear_approval(self):
        self._guarded().write({"approved_by_id": False, "approved_at": False})

    @api.model
    def _inv_threshold(self, key):
        return inv_param(self.env, key, 0.0)
