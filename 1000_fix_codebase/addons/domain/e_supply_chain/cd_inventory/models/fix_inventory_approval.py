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
SUPERVISOR_GROUP = "cd_wms_structure.group_warehouse_supervisor"
TECHNICIAN_GROUP = "cd_wms_structure.group_van_technician"
# A06 final pass B18 (spec section 13): cost and value fields carry this group,
# so a field read outside it is refused by the ORM and the workspace columns
# and forms leave it out. The ledger's own code reads cost as sudo.
COST_GROUP = "cd_wms_structure.group_stock_cost_viewer"
# A06 final pass B5 (spec section 13): R06 approves transfers and variance
# resolution of its own branch, R26 adjustments and write-offs.
APPROVER_BRANCH_GROUP = "cd_wms_structure.group_inventory_approver_branch"
APPROVER_FINANCE_GROUP = "cd_wms_structure.group_inventory_approver_finance"
# A06 final pass B10: who may see a van's expected quantity and variance
VAN_VARIANCE_GROUPS = "%s,%s,%s" % (CONTROLLER_GROUP, APPROVER_BRANCH_GROUP, APPROVER_FINANCE_GROUP)

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


def sees_cost(env) -> bool:
    """Unit cost and stock value are field-restricted (spec section 13)."""
    return env.su or env.user.has_group(COST_GROUP)


def is_supervisor(env) -> bool:
    return env.su or env.user.has_group(SUPERVISOR_GROUP)


def require_supervisor(env, what):
    """The M41 supervisor grant (spec section 13): wave release, task
    reassignment, and the exception of picking without scans."""
    if not is_supervisor(env):
        raise AccessError("Only a Warehouse Supervisor can %s." % what)


def part_codes(part) -> set:
    """What a scan of this part may read: barcode, QR or part number."""
    return {c for c in (part.barcode, part.qr_code, part.part_number) if c}


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

    def _inv_approver_groups(self) -> tuple:
        """The roles that decide this document (spec section 13). A model
        widens it; the Inventory Controller decides everything."""
        return (CONTROLLER_GROUP,)

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
        if not any(user.has_group(group) for group in self._inv_approver_groups()):
            raise AccessError(
                "Only an Inventory Controller can approve %s."
                % ", ".join(rec._inv_approval_label() for rec in self)
            )
        # R06 approves within its own branch: the company and OU rules decide
        if not user.has_group(CONTROLLER_GROUP) and not user.has_group(APPROVER_FINANCE_GROUP):
            self.check_access("read")
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


# ---------------------------------------------------------------------------
# A06 M15-2 / BRU-INV-11/24: a write-off or adjustment above the controller's
# limit is ALSO a routed M63 approval on the DOFA ladder by value. The spec
# (M15 BRU-INV-11/24) sets the matrix: up to BDT 25,000 the Inventory
# Manager (here: the Inventory Controller two-person rule), above it the
# CFO (DOFA Tier 4). Both bands are configuration; the default ceiling is
# open (everything above the controller limit is a CFO decision) unless
# PARAM_DOFA_CFO_MAX is set, above which it goes to Tier 5.
PARAM_DOFA_CONTROLLER_MAX = "cd_inventory.writeoff_dofa_controller_max"
PARAM_DOFA_CFO_MAX = "cd_inventory.writeoff_dofa_cfo_max"
DEFAULT_DOFA_CONTROLLER_MAX = 25000.0

DOFA_TIER_GROUP = {
    "tier_1": "cd_entity_config.group_dofa_tier_1",
    "tier_2": "cd_entity_config.group_dofa_tier_2",
    "tier_3": "cd_entity_config.group_dofa_tier_3",
    "tier_4": "cd_entity_config.group_dofa_tier_4",
    "tier_5": "cd_entity_config.group_dofa_tier_5",
}


def writeoff_ladder(env):
    controller_max = inv_param(env, PARAM_DOFA_CONTROLLER_MAX, DEFAULT_DOFA_CONTROLLER_MAX)
    cfo_max = inv_param(env, PARAM_DOFA_CFO_MAX, 0.0)
    ladder = [(controller_max, "tier_0")]
    if cfo_max > controller_max:
        ladder.append((cfo_max, "tier_4"))
        ladder.append((float("inf"), "tier_5"))
    else:
        ladder.append((float("inf"), "tier_4"))
    return ladder


class FixInventoryWriteoffDofaMixin(models.AbstractModel):
    """The routed DOFA leg of an inventory write-off / adjustment. The model
    gives `_writeoff_value()`; amounts at or below the write-off approval
    threshold carry no DOFA amount (the two-person rule alone decides)."""

    _name = "fix.inventory.writeoff.dofa.mixin"
    _inherit = ["fix.dofa.mixin", "fix.inventory.approval.mixin"]
    _description = "Inventory Write-off DOFA (routed)"

    _approval_domain = "inventory_writeoff"
    _approval_apply_method = "action_dofa_approve"
    _approval_routed = True

    def _writeoff_value(self) -> float:
        return 0.0

    def _dofa_amount(self) -> float:
        self.ensure_one()
        value = abs(self._writeoff_value() or 0.0)
        if value <= inv_param(self.env, PARAM_WRITEOFF_THRESHOLD, 0.0) + 1e-6:
            return 0.0
        return value

    def _dofa_thresholds(self):
        return writeoff_ladder(self.env)

    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def _inv_needs_dofa(self) -> bool:
        self.ensure_one()
        return self._dofa_current_tier() != "tier_0"

    # ---- local defences (the M63 rule book is user-writable, A11 M63-2) ----
    def _approval_group_for(self, rule, tier):
        xmlid = DOFA_TIER_GROUP.get(tier) if tier else None
        return self.env.ref(xmlid, raise_if_not_found=False) if xmlid else None

    def _inv_dofa_conflicts(self):
        self.ensure_one()
        rec = self.sudo()
        return (
            rec.create_uid
            | rec.requested_by_id
            | rec.approved_by_id
            | rec.approval_amount_changed_by_id
            | rec._inv_excluded_users()
        )

    def _approval_excluded(self):
        return (super()._approval_excluded() | self._inv_dofa_conflicts()).sudo()

    def _inv_dofa_apply(self):
        """Per model: what the routed approval releases (post, scrap)."""
        return None

    def action_dofa_approve(self):
        """Only from the approver's M63 inbox task, by the tier holder, never
        by the counter / requester / controller / creator; then the
        write-off the approval covers is applied (pinned to its value)."""
        self._approval_assert_routed()
        for rec in self:
            if not self.env.su:
                task = rec._approval_task()
                deciders = self.env.user | task.on_behalf_of_id
                clash = deciders & rec._inv_dofa_conflicts()
                if clash:
                    raise UserError(
                        "Segregation of duties: %s raised, counted, approved or changed %s "
                        "and cannot give its DOFA approval."
                        % (", ".join(clash.mapped("name")), rec.display_name)
                    )
        result = super(FixInventoryWriteoffDofaMixin, self.sudo()).action_dofa_approve()
        for rec in self.sudo():
            rec._dofa_assert_approved("The write-off of %s" % rec.display_name)
            rec._inv_dofa_apply()
        return result

    def _inv_route_dofa(self, justification):
        """Hand the write-off to M63 after the controller's approval."""
        for rec in self:
            rec.action_request_approval(justification=justification)
