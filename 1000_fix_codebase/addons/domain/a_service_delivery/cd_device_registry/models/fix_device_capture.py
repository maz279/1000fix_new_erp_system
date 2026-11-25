# fix_device_capture — M17 capture pass 2 (19 Nov 2026).
#
# The 13 Nov pass gave every M17 sub-module page a "+ New". Read against the
# spec (FR-AST-001..052, BRU-AST-01..23), seven pages still could not record a
# record the spec places on them, because the record did not exist:
#
# - p1  FR-AST-008 asset label (QR tag, re-label keeps the old tag) and
#       FR-AST-002/010 identifiers beyond serial/IMEI (brand service tag,
#       customer asset number, part number), a shared value raising a conflict.
# - p2  FR-AST-015 accessory register (P0): what came in with the device, which
#       BRU-AST-08 reconciles before release; FR-AST-012 actual configuration
#       with its history.
# - p3  FR-AST-022 population (P0) and its reason-coded change (BRU-AST-10/11).
# - p7  BRU-AST-16 warranty derivation basis; a defaulted date is not verified.
# - p8  FR-AST-038 estate nodes (site > department > user) and dated placements.
# - p10 FR-AST-048 end-of-life routing decision with approver (BRU-AST-19).
# - p11 FR-AST-051 stewardship worklist with ageing and escalation (BRU-AST-22).
#
# Outcomes go to the device's chatter and history; no new bus events.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_device import (
    BRANCH_MANAGER_GROUP,
    NOT_SCRAPPABLE,
    QUALITY_MANAGER_GROUP,
    REGISTRY_AGENT_GROUP,
)
from .fix_device_ops import _BOOKKEEPING, RELEASE_EVENTS, _latest_today

# FR-AST-022: exactly one population per asset.
POPULATIONS = [
    ("customer_owned", "Customer-owned"),
    ("rental_pool", "Rental pool"),
    ("refurbishment_stock", "Refurbishment stock"),
    ("trade_in_intake", "Trade-in intake"),
    ("marketplace_listed", "Marketplace-listed"),
    ("ewaste_pending", "E-waste pending"),
    ("company_issued", "Company-issued to customer"),
]
# BRU-AST-11: these are 1000FiX's stock; they become customer-owned only with
# an ownership-transfer transaction.
COMPANY_POPULATIONS = ("rental_pool", "refurbishment_stock")
POPULATION_REASONS = [
    ("trade_in", "Trade-in received"),
    ("refurbishment_intake", "Taken into refurbishment"),
    ("rental_onboarding", "Added to the rental pool"),
    ("rental_offboarding", "Taken out of the rental pool"),
    ("marketplace_listing", "Listed on the marketplace"),
    ("ewaste_routing", "Routed to e-waste"),
    ("sale_to_customer", "Sold to a customer"),
    ("company_issue", "Issued by the company to a customer"),
    ("return_to_customer", "Returned to its customer"),
    ("eol_decision", "End-of-life decision"),
    ("correction", "Correction of a wrong classification"),
]
# FR-AST-002: identifiers beyond the serial and IMEIs held on the device.
EXTRA_IDENTIFIER_TYPES = [
    ("asset_tag", "1000FiX Asset Tag"),
    ("brand_service_tag", "Brand Service Tag"),
    ("customer_asset_no", "Customer Asset Number"),
    ("part_number", "Part Number"),
]
TYPED_IDENTIFIERS = ("brand_service_tag", "customer_asset_no", "part_number")
WARRANTY_BASES = [
    ("purchase_evidence", "Purchase evidence (receipt / invoice)"),
    ("brand_lookup", "Brand lookup (OEM portal / service tag)"),
    ("contract", "Contract or plan document"),
    ("manufacture_default", "Default from date of manufacture"),
]
# BRU-AST-19 / FR-AST-048: the route, and the customer instruction it needs.
EOL_ROUTES = [
    ("refurbish", "Refurbish and resell (M14)"),
    ("dispose", "Lawful disposal (M18)"),
    ("return_to_customer", "Return to customer as is"),
]
EOL_INSTRUCTION_FOR_ROUTE = {
    "refurbish": "refurbish",
    "dispose": "recycle",
    "return_to_customer": "return_as_is",
}
STEWARD_PROVISIONAL_DAYS_PARAM = "cd_device_registry.steward_provisional_days"
STEWARD_PROVISIONAL_DAYS_DEFAULT = 7
STEWARD_ESCALATION_DAYS_PARAM = "cd_device_registry.steward_escalation_days"
STEWARD_ESCALATION_DAYS_DEFAULT = 14
# A07 ERP audit (2026-11-20) M17-17, spec §13: R05 (Operations Director)
# approves population changes. A requested change applies only on approval by
# a holder who did not request it.
POPULATION_APPROVER_GROUP = "cd_device_registry.group_device_population_approver"
# M17-12, BRU-AST-05: identifier conflicts and duplicates are the Quality
# Manager's (R32) to resolve.
QM_ISSUE_TYPES = ("conflict", "duplicate")


def _norm(value) -> str:
    return "".join((value or "").split()).upper()


def _int_param(env, key, default) -> int:
    try:
        return max(int(env["ir.config_parameter"].sudo().get_param(key, default)), 1)
    except (TypeError, ValueError):
        return default


def _seq(env, code, fallback):
    return env["ir.sequence"].sudo().next_by_code(code) or fallback


def _changed(rec, vals) -> bool:
    """True when `vals` would change a business value of `rec`. Echoing the
    current value (the P03 form posts every field it shows) is no change."""
    names = [n for n in set(vals) - _BOOKKEEPING if n in rec._fields]
    return any(rec._fix_guard_differs(n, vals[n], rec[n]) for n in names)


class _PermanentMixin(models.AbstractModel):
    """Insert-only for users: no edit, no delete. Service code is trusted."""

    _name = "fix.device.permanent.mixin"
    _description = "M17 Permanent Record"
    _inherit = ["fix.guarded.mixin"]
    _permanent_hint = "Record the next one instead."

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id:
            locked |= {
                n
                for n, f in self._fields.items()
                if f.store
                and n not in {"id", "create_uid", "create_date", "write_uid", "write_date"}
            }
        return locked

    def write(self, vals):
        if not self._fix_guard_open() and any(_changed(rec, vals) for rec in self):
            raise UserError(
                "%s is a permanent record and is never edited. %s"
                % (self._description, self._permanent_hint)
            )
        return super().write(vals)

    def unlink(self):
        if not self._fix_guard_open():
            raise UserError("%s is a permanent record and is never deleted." % self._description)
        return super().unlink()


def _not_future(rec, value, what):
    if value and value > _latest_today(rec):
        raise ValidationError("%s cannot be in the future (%s)." % (what, value))


# =============================================================================
# The device: population, estate node, asset tag, extra identifiers
# =============================================================================
class FixDeviceCapture(models.Model):
    _inherit = "fix.device"
    _rec_names_search = [
        "name",
        "serial_number",
        "imei_1",
        "imei_2",
        "legacy_reference",
        "asset_tag",
    ]

    population = fields.Selection(
        POPULATIONS,
        string="Population",
        default="customer_owned",
        required=True,
        index=True,
        tracking=True,
        help="FR-AST-022: which modules may act on the device. Changed only by a "
        "reason-coded Population Change.",
    )
    population_changed_at = fields.Datetime(
        string="Population Changed At", readonly=True, copy=False
    )
    estate_node_id = fields.Many2one(
        "fix.device.estate.node",
        string="Estate Node",
        index=True,
        ondelete="restrict",
        copy=False,
        help="FR-AST-038: the site, department or user the device is placed at. Moved "
        "only by an Estate Placement.",
    )
    asset_tag = fields.Char(
        string="1000FiX Asset Tag",
        index=True,
        readonly=True,
        copy=False,
        help="The code on the device's active QR label (FR-AST-008).",
    )
    accessory_held_count = fields.Integer(
        string="Accessories Held", compute="_compute_accessory_held_count"
    )
    # FR-AST-002: staged by the Add Identifier form, applied by
    # action_add_identifier, cleared afterwards.
    extra_identifier_type = fields.Selection(
        [t for t in EXTRA_IDENTIFIER_TYPES if t[0] in TYPED_IDENTIFIERS],
        string="Identifier Type",
        store=False,
    )
    extra_identifier_value = fields.Char(string="Identifier Value", store=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "population",
            "population_changed_at",
            "estate_node_id",
            "asset_tag",
        }

    def _compute_accessory_held_count(self):
        Accessory = self.env["fix.device.accessory"].sudo()
        groups = Accessory._read_group(
            [("device_id", "in", self.ids), ("state", "=", "held")], ["device_id"], ["__count"]
        )
        counts = {device.id: count for device, count in groups}
        for rec in self:
            rec.accessory_held_count = counts.get(rec.id, 0)

    # ---- estate placements are the dated history of estate_id ----------------
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if not self.env.context.get("fix_from_placement"):
            records.filtered("estate_id")._placement_follow_estate(
                "Placed at registration", records.browse()
            )
        return records

    def write(self, vals):
        before = {rec.id: rec.estate_id for rec in self} if "estate_id" in vals else {}
        result = super().write(vals)
        if before and not self.env.context.get("fix_from_placement"):
            moved = self.filtered(lambda r: r.estate_id != before.get(r.id))
            if moved:
                moved._placement_follow_estate(
                    self.env.context.get("fix_placement_reason") or "Changed on the asset record",
                    moved,
                )
        return result

    def _placement_follow_estate(self, reason, closing):
        """The device's estate changed outside an Estate Placement (the asset
        form, a bulk load, a transfer out of the client): the dated placement
        history follows, and a node of the old estate is dropped."""
        Placement = self.env["fix.device.estate.placement"].sudo()._guarded()
        today = fields.Date.context_today(self)
        for rec in self:
            if rec in closing:
                Placement.search([("device_id", "=", rec.id), ("is_current", "=", True)])._close(
                    today
                )
            if rec.estate_node_id and rec.estate_node_id.estate_id != rec.estate_id:
                rec.sudo()._guarded().with_context(fix_from_placement=True).write(
                    {"estate_node_id": False}
                )
            if rec.estate_id:
                Placement.with_context(fix_from_placement=True).create(
                    {
                        "device_id": rec.id,
                        "estate_id": rec.estate_id.id,
                        "placed_from": today,
                        "move_reason": reason,
                    }
                )

    # ---- FR-AST-002 / FR-AST-010: further identifiers ------------------------
    def action_add_identifier(self, identifier_type=None, value=None):
        """Record a brand service tag, customer asset number or part number
        against the device. The same value of the same type already current on
        another device is still recorded (it is what the customer presented),
        and both devices go on the stewardship worklist as a conflict."""
        self.ensure_one()
        identifier_type = identifier_type or self.extra_identifier_type
        value = (value or self.extra_identifier_value or "").strip()
        if identifier_type not in TYPED_IDENTIFIERS:
            raise UserError(
                "Choose the identifier type: brand service tag, customer asset number or part "
                "number. Serials and IMEIs are captured on the asset itself; the asset tag comes "
                "from a label."
            )
        if not value:
            raise UserError("Give the identifier value.")
        self.check_access("write")
        if self.state == "scrapped":
            raise UserError("%s is scrapped; no identifier is added to it." % self.display_name)
        Identifier = self.env["fix.device.identifier"].sudo()._guarded()
        normal = _norm(value)
        own = Identifier.search(
            [
                ("device_id", "=", self.id),
                ("identifier_type", "=", identifier_type),
                ("value_normalised", "=", normal),
                ("is_current", "=", True),
            ],
            limit=1,
        )
        if own:
            raise UserError("%s already carries %s." % (self.display_name, value))
        others = Identifier.search(
            [
                ("device_id", "!=", self.id),
                ("device_id.active", "=", True),
                ("identifier_type", "=", identifier_type),
                ("value_normalised", "=", normal),
                ("is_current", "=", True),
            ]
        )
        row = Identifier.create(
            {
                "device_id": self.id,
                "identifier_type": identifier_type,
                "value": value,
                "value_normalised": normal,
                "source": "capture",
                "captured_by_id": self.env.uid,
                "captured_at": fields.Datetime.now(),
            }
        )
        label = dict(EXTRA_IDENTIFIER_TYPES)[identifier_type]
        self.message_post(body="%s %s recorded by %s." % (label, value, self.env.user.name))
        if others:
            involved = self | others.device_id
            involved.sudo()._a07_quarantine(
                "%s %s is on %s" % (label, value, ", ".join(involved.mapped("display_name")))
            )
            self._publish(
                "device.identifier_conflict",
                {
                    "device_id": self.id,
                    "identifier_type": identifier_type,
                    "value": value,
                    "other_device_ids": others.device_id.ids,
                    "recorded_by": self.env.uid,
                },
            )
            Issue = self.env["fix.device.quality.issue"].sudo()._guarded()
            for device in involved:
                Issue.create(
                    {
                        "device_id": device.id,
                        "issue_type": "conflict",
                        "severity": "high",
                        "description": "%s %s is on %s (BRU-AST-05): resolve which device it "
                        "belongs to; a possible counterfeit or grey-market unit."
                        % (
                            label,
                            value,
                            ", ".join((self | others.device_id).mapped("display_name")),
                        ),
                        "assigned_branch_id": device.branch_id.id or False,
                    }
                )
        return row

    def _population_label(self):
        return dict(POPULATIONS).get(self.population, self.population)


class FixDeviceIdentifierTypes(models.Model):
    _inherit = "fix.device.identifier"

    identifier_type = fields.Selection(
        selection_add=EXTRA_IDENTIFIER_TYPES,
        ondelete={key: "cascade" for key, _label in EXTRA_IDENTIFIER_TYPES},
    )


# =============================================================================
# p1 · FR-AST-008 asset labels
# =============================================================================
class FixDeviceLabel(models.Model):
    _name = "fix.device.label"
    _description = "Device Asset Label"
    _inherit = ["fix.device.permanent.mixin"]
    _order = "applied_on desc, id desc"
    _permanent_hint = "A damaged tag is replaced by applying a new label, which keeps this one."

    name = fields.Char(string="Label Code", required=True, default="New", copy=False, index=True)
    device_id = fields.Many2one(
        "fix.device", string="Device", required=True, ondelete="cascade", index=True
    )
    label_type = fields.Selection(
        [("qr", "QR tag"), ("barcode", "Barcode tag"), ("nfc", "NFC tag")],
        string="Label Type",
        required=True,
        default="qr",
    )
    applied_by_id = fields.Many2one(
        "hr.employee", string="Labelling Technician", required=True, index=True
    )
    applied_on = fields.Date(string="Applied On", required=True, default=fields.Date.context_today)
    printed_at = fields.Datetime(string="Printed At", default=fields.Datetime.now, readonly=True)
    replaces_label_id = fields.Many2one(
        "fix.device.label", string="Replaces Label", readonly=True, copy=False
    )
    replace_reason = fields.Char(
        string="Why the Old Tag Is Replaced",
        help="Required when the device already carries an active label.",
    )
    state = fields.Selection(
        [("active", "Active"), ("replaced", "Replaced")],
        default="active",
        required=True,
        readonly=True,
        index=True,
    )
    replaced_on = fields.Date(string="Replaced On", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "replaced_on", "replaces_label_id"}

    _label_code_unique = models.Constraint(
        "UNIQUE (name)", "This label code is already issued to another device."
    )

    @api.model_create_multi
    def create(self, vals_list):
        trusted = self._fix_guard_open()
        prepared = []
        for vals in vals_list:
            if not trusted:
                for name in self._fix_guarded_fields():
                    vals.pop(name, None)
            device = self.env["fix.device"].browse(vals.get("device_id") or 0).exists()
            if not device:
                raise UserError("Choose the device the label is applied to.")
            if device.state == "scrapped":
                raise UserError("%s is scrapped; it is not labelled." % device.display_name)
            current = self.sudo().search(
                [("device_id", "=", device.id), ("state", "=", "active")], limit=1
            )
            if current and not (vals.get("replace_reason") or "").strip() and not trusted:
                raise UserError(
                    "%s already carries label %s. Say why it is replaced (damaged, lost, "
                    "unreadable); the old tag stays on record."
                    % (device.display_name, current.name)
                )
            if vals.get("name", "New") in (False, "", "New"):
                vals["name"] = _seq(self.env, "fix.device.label", "FXT-New")
            vals["replaces_label_id"] = current.id or False
            prepared.append(current)
        # replaces_label_id is the registry's to set, so the insert takes the token
        records = super(FixDeviceLabel, self._guarded()).create(vals_list).with_env(self.env)
        Identifier = self.env["fix.device.identifier"].sudo()._guarded()
        now = fields.Datetime.now()
        for rec, current in zip(records, prepared, strict=True):
            _not_future(rec, rec.applied_on, "The label date")
            if current:
                current.sudo()._guarded().write(
                    {"state": "replaced", "replaced_on": rec.applied_on}
                )
                Identifier.search(
                    [
                        ("device_id", "=", rec.device_id.id),
                        ("identifier_type", "=", "asset_tag"),
                        ("is_current", "=", True),
                    ]
                ).write(
                    {
                        "is_current": False,
                        "superseded_at": now,
                        "superseded_by_id": self.env.uid,
                        "supersede_reason": rec.replace_reason or "Label replaced",
                    }
                )
            Identifier.create(
                {
                    "device_id": rec.device_id.id,
                    "identifier_type": "asset_tag",
                    "value": rec.name,
                    "value_normalised": _norm(rec.name),
                    "source": "capture",
                    "captured_by_id": self.env.uid,
                    "captured_at": now,
                }
            )
            rec.device_id.sudo()._guarded().write({"asset_tag": rec.name})
            rec.device_id.message_post(
                body="Asset label %s applied by %s%s."
                % (
                    rec.name,
                    rec.applied_by_id.name,
                    (", replacing %s (%s)" % (current.name, rec.replace_reason)) if current else "",
                )
            )
        return records


# =============================================================================
# p2 · FR-AST-015 accessory register (BRU-AST-08) and FR-AST-012 configuration
# =============================================================================
ACCESSORY_TYPES = [
    ("charger", "Charger / adapter"),
    ("battery", "Battery"),
    ("cable", "Cable"),
    ("bag", "Bag / case"),
    ("stylus", "Stylus"),
    ("remote", "Remote control"),
    ("sim_card", "SIM card"),
    ("memory_card", "Memory card"),
    ("box", "Original box"),
    ("other", "Other"),
]


class FixDeviceAccessory(models.Model):
    """One accessory received with the device. It is held until it is handed
    back or recorded missing; a device is not released to its customer while
    an accessory is still held (BRU-AST-08)."""

    _name = "fix.device.accessory"
    _description = "Accessory Received with a Device"
    _inherit = ["fix.guarded.mixin"]
    _order = "received_on desc, id desc"

    name = fields.Char(string="Reference", required=True, default="New", copy=False)
    device_id = fields.Many2one(
        "fix.device", string="Device", required=True, ondelete="cascade", index=True
    )
    intake_reference = fields.Char(
        string="Intake / Job Reference", help="The service order or intake slip it came with."
    )
    accessory_type = fields.Selection(ACCESSORY_TYPES, string="Accessory", required=True)
    description = fields.Char(string="Description", help="Make, colour, condition.")
    quantity = fields.Integer(string="Quantity", required=True, default=1)
    received_on = fields.Date(
        string="Received On", required=True, default=fields.Date.context_today
    )
    received_by_id = fields.Many2one(
        "res.users", string="Received By", readonly=True, default=lambda self: self.env.uid
    )
    state = fields.Selection(
        [("held", "Held"), ("returned", "Returned"), ("missing", "Missing at Return")],
        default="held",
        required=True,
        readonly=True,
        index=True,
    )
    returned_on = fields.Date(string="Returned On", readonly=True, copy=False)
    returned_by_id = fields.Many2one("res.users", string="Returned By", readonly=True, copy=False)
    discrepancy_note = fields.Char(string="Discrepancy", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "returned_on",
            "returned_by_id",
            "discrepancy_note",
            "received_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id:
            locked |= {"device_id", "accessory_type", "quantity", "received_on", "intake_reference"}
        return locked

    @api.constrains("quantity")
    def _check_quantity(self):
        for rec in self:
            if rec.quantity < 1:
                raise ValidationError(
                    "An accessory is received at least once (quantity 1 or more)."
                )

    @api.constrains("received_on")
    def _check_received_on(self):
        for rec in self:
            _not_future(rec, rec.received_on, "The receipt date")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            device = self.env["fix.device"].browse(vals.get("device_id") or 0).exists()
            if device and device.state == "scrapped" and not self._fix_guard_open():
                raise UserError(
                    "%s is scrapped; nothing is received with it." % device.display_name
                )
            if vals.get("name", "New") in (False, "", "New"):
                vals["name"] = _seq(self.env, "fix.device.accessory", "DACC/New")
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open():
            locked = {"device_id", "accessory_type", "quantity", "received_on", "intake_reference"}
            for rec in self:
                if rec.state != "held" and any(
                    rec._fix_guard_differs(n, vals[n], rec[n])
                    for n in set(vals) & set(rec._fields) - _BOOKKEEPING
                ):
                    raise UserError("%s is %s and is no longer edited." % (rec.name, rec.state))
                if any(rec._fix_guard_differs(n, vals[n], rec[n]) for n in locked & set(vals)):
                    raise UserError(
                        "What was received is recorded once. Record it missing at return, or "
                        "record another accessory."
                    )
        return super().write(vals)

    def unlink(self):
        if not self._fix_guard_open():
            raise UserError(
                "A received accessory stays on record; it is returned or recorded missing."
            )
        return super().unlink()

    def _assert_held(self):
        for rec in self:
            if rec.state != "held":
                raise UserError(
                    "%s is already %s."
                    % (rec.name, dict(rec._fields["state"].selection)[rec.state])
                )
            rec.device_id.check_access("write")

    def action_return(self):
        self._assert_held()
        today = fields.Date.context_today(self)
        for rec in self:
            rec._guarded().write(
                {"state": "returned", "returned_on": today, "returned_by_id": self.env.uid}
            )
        return True

    def action_report_missing(self, reason=None):
        if not (reason or "").strip():
            raise UserError("Say what is missing or different, and what the customer was told.")
        self._assert_held()
        today = fields.Date.context_today(self)
        for rec in self:
            rec._guarded().write(
                {
                    "state": "missing",
                    "returned_on": today,
                    "returned_by_id": self.env.uid,
                    "discrepancy_note": reason.strip(),
                }
            )
            rec.device_id.message_post(
                body="Accessory %s (%s) missing at return: %s"
                % (rec.name, dict(ACCESSORY_TYPES)[rec.accessory_type], reason.strip())
            )
        return True


class FixDeviceCustodyAccessoryGate(models.Model):
    _inherit = "fix.device.custody"

    @api.model
    def _check_release(self, vals):
        """BRU-AST-08: the accessory reconciliation is the register's, not a
        tick: a device goes back to its customer only when every accessory
        received with it is returned or recorded missing."""
        super()._check_release(vals)
        if vals.get("event") not in RELEASE_EVENTS:
            return
        held = (
            self.env["fix.device.accessory"]
            .sudo()
            .search([("device_id", "=", vals.get("device_id")), ("state", "=", "held")])
        )
        if held:
            raise UserError(
                "%s still has %d accessor%s held (%s): return each one or record it missing "
                "before release (BRU-AST-08)."
                % (
                    held[0].device_id.display_name,
                    len(held),
                    "y" if len(held) == 1 else "ies",
                    ", ".join(held.mapped("name")),
                )
            )


CONFIG_ATTRIBUTES = [
    ("memory", "Memory (RAM)"),
    ("storage", "Storage"),
    ("processor", "Processor"),
    ("display", "Display"),
    ("battery", "Battery"),
    ("firmware", "Firmware / BIOS"),
    ("os", "Operating System"),
    ("option", "Installed Option"),
]
# Several options can be installed at once; every other attribute has one value.
MULTI_VALUE_ATTRIBUTES = ("option",)


class FixDeviceConfiguration(models.Model):
    """The unit's actual specification where it differs from its model; a new
    value of an attribute closes the previous one, which stays as history."""

    _name = "fix.device.configuration"
    _description = "Device Actual Configuration"
    _inherit = ["fix.device.permanent.mixin"]
    _order = "device_id, attribute, effective_from desc, id desc"
    _permanent_hint = (
        "A changed value is recorded as a new configuration row, which closes this one."
    )

    device_id = fields.Many2one(
        "fix.device", string="Device", required=True, ondelete="cascade", index=True
    )
    attribute = fields.Selection(CONFIG_ATTRIBUTES, string="Attribute", required=True)
    value = fields.Char(string="Value", required=True)
    unit = fields.Char(string="Unit", help="GB, GHz, inch, mAh…")
    source = fields.Selection(
        [
            ("intake", "Seen at intake"),
            ("diagnostic", "Diagnostic report"),
            ("customer", "Declared by the customer"),
            ("brand", "Brand record"),
        ],
        string="Source",
        required=True,
        default="intake",
    )
    effective_from = fields.Date(
        string="Effective From", required=True, default=fields.Date.context_today
    )
    effective_to = fields.Date(string="Effective To", readonly=True, copy=False)
    is_current = fields.Boolean(string="Current", default=True, readonly=True, index=True)
    recorded_by_id = fields.Many2one(
        "res.users", string="Recorded By", readonly=True, default=lambda self: self.env.uid
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"effective_to", "is_current", "recorded_by_id"}

    @api.depends("device_id", "attribute", "value", "unit")
    def _compute_display_name(self):
        # the model has no name field: a picker or chip would show "model,id"
        labels = dict(CONFIG_ATTRIBUTES)
        for rec in self:
            rec.display_name = "%s · %s: %s%s" % (
                rec.device_id.display_name or "",
                labels.get(rec.attribute, rec.attribute or ""),
                rec.value or "",
                (" " + rec.unit) if rec.unit else "",
            )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            _not_future(rec, rec.effective_from, "The effective date")
            if rec.device_id.state == "scrapped" and not self._fix_guard_open():
                raise UserError("%s is scrapped." % rec.device_id.display_name)
            if rec.attribute in MULTI_VALUE_ATTRIBUTES:
                continue
            previous = self.sudo().search(
                [
                    ("device_id", "=", rec.device_id.id),
                    ("attribute", "=", rec.attribute),
                    ("is_current", "=", True),
                    ("id", "!=", rec.id),
                ]
            )
            for old in previous:
                if old.effective_from > rec.effective_from:
                    raise ValidationError(
                        "%s of %s is already recorded from %s; a new value cannot start earlier "
                        "(%s)."
                        % (
                            dict(CONFIG_ATTRIBUTES)[rec.attribute],
                            rec.device_id.display_name,
                            old.effective_from,
                            rec.effective_from,
                        )
                    )
            previous._guarded().write({"is_current": False, "effective_to": rec.effective_from})
        return records


# =============================================================================
# p3 · FR-AST-022 population and its reason-coded change (BRU-AST-10/11)
# =============================================================================
class FixDevicePopulationChange(models.Model):
    _name = "fix.device.population.change"
    _description = "Device Population Change"
    _inherit = ["fix.device.permanent.mixin"]
    _order = "recorded_at desc, id desc"
    _permanent_hint = "A wrong change is put right by another change with the reason Correction."

    name = fields.Char(string="Reference", required=True, default="New", copy=False)
    device_id = fields.Many2one(
        "fix.device", string="Device", required=True, ondelete="cascade", index=True
    )
    from_population = fields.Selection(POPULATIONS, string="From", readonly=True)
    to_population = fields.Selection(POPULATIONS, string="To", required=True)
    reason_code = fields.Selection(POPULATION_REASONS, string="Reason", required=True)
    notes = fields.Char(string="Notes")
    ownership_id = fields.Many2one(
        "fix.device.ownership",
        string="Ownership Transfer",
        help="BRU-AST-11: rental-pool or refurbishment stock becomes customer-owned only "
        "with the ownership transfer that sold or gave it.",
    )
    recorded_by_id = fields.Many2one(
        "res.users", string="Recorded By", readonly=True, default=lambda self: self.env.uid
    )
    recorded_at = fields.Datetime(string="Recorded At", readonly=True, default=fields.Datetime.now)
    # A07 ERP audit M17-17: a person's change is requested, and applies only
    # when an Operations Director (R05) who did not request it approves it.
    # A change the registry makes itself (a transfer, an end-of-life route, a
    # trade-in or recycling event) is applied at once.
    state = fields.Selection(
        [("requested", "Awaiting Approval"), ("applied", "Applied"), ("rejected", "Rejected")],
        string="Status",
        default="applied",
        required=True,
        readonly=True,
        index=True,
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True, copy=False)
    approved_at = fields.Datetime(string="Approved At", readonly=True, copy=False)
    decision_note = fields.Char(string="Decision Note", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "from_population",
            "recorded_by_id",
            "recorded_at",
            "state",
            "approved_by_id",
            "approved_at",
            "decision_note",
        }

    @api.model_create_multi
    def create(self, vals_list):
        trusted = self._fix_guard_open()
        for vals in vals_list:
            if not trusted:
                for name in self._fix_guarded_fields():
                    vals.pop(name, None)
            device = self.env["fix.device"].browse(vals.get("device_id") or 0).exists()
            if not device:
                raise UserError("Choose the device whose population changes.")
            if not trusted:
                device._assert_role(REGISTRY_AGENT_GROUP, "Changing a device's population")
                device.check_access("write")
            target = vals.get("to_population")
            if target == device.population:
                raise UserError(
                    "%s is already %s." % (device.display_name, device._population_label())
                )
            if device.state == "scrapped" and not trusted:
                raise UserError(
                    "%s is scrapped; its population no longer changes." % device.display_name
                )
            if (
                device.population in COMPANY_POPULATIONS
                and target == "customer_owned"
                and not trusted
            ):
                self._check_ownership_evidence(device, vals.get("ownership_id"))
            vals["from_population"] = device.population
            if not trusted:
                pending = self.sudo().search(
                    [("device_id", "=", device.id), ("state", "=", "requested")], limit=1
                )
                if pending:
                    raise UserError(
                        "%s already has a population change awaiting approval (%s)."
                        % (device.display_name, pending.name)
                    )
                vals["state"] = "requested"
            else:
                vals.setdefault("state", "applied")
            if vals.get("name", "New") in (False, "", "New"):
                vals["name"] = _seq(self.env, "fix.device.population.change", "DPOP/New")
        # from_population is the registry's to set, so the insert takes the token
        records = (
            super(FixDevicePopulationChange, self._guarded()).create(vals_list).with_env(self.env)
        )
        for rec in records:
            if rec.state == "applied":
                rec._apply()
            else:
                rec.device_id.message_post(
                    body="Population change %s → %s requested by %s: awaiting an Operations "
                    "Director's approval."
                    % (
                        dict(POPULATIONS).get(rec.from_population),
                        rec._to_label(),
                        rec.recorded_by_id.name,
                    )
                )
        return records

    def _to_label(self):
        return dict(POPULATIONS).get(self.to_population, self.to_population)

    def _apply(self):
        """Move the device's population and tell M49/M13/M14/M15
        (device.population_changed, with the approver)."""
        self.ensure_one()
        self.device_id.sudo()._guarded().write(
            {"population": self.to_population, "population_changed_at": fields.Datetime.now()}
        )
        labels = dict(POPULATIONS)
        self.device_id.message_post(
            body="Population %s → %s (%s) by %s%s%s."
            % (
                labels.get(self.from_population),
                labels.get(self.to_population),
                dict(POPULATION_REASONS)[self.reason_code],
                self.recorded_by_id.name,
                (", approved by %s" % self.approved_by_id.name) if self.approved_by_id else "",
                (": %s" % self.notes) if self.notes else "",
            )
        )
        self.device_id._publish(
            "device.population_changed",
            {
                "device_id": self.device_id.id,
                "change_id": self.id,
                "from_population": self.from_population or None,
                "to_population": self.to_population,
                "reason_code": self.reason_code,
                "ownership_id": self.ownership_id.id or None,
                "recorded_by": self.recorded_by_id.id or None,
                "approved_by": self.approved_by_id.id or None,
            },
        )

    def _assert_approver(self):
        self.ensure_one()
        if self.env.su:
            return
        if not self.env.user.has_group(POPULATION_APPROVER_GROUP):
            raise UserError(
                "A population change is approved by an Operations Director (R05), which %s is "
                "not." % self.env.user.name
            )
        if self.env.user in (self.recorded_by_id | self.create_uid):
            raise UserError(
                "Segregation of duties: you requested %s, so another Operations Director "
                "approves it." % self.name
            )

    def action_approve(self):
        for rec in self:
            if rec.state != "requested":
                raise UserError("%s is not awaiting approval." % rec.name)
            rec._assert_approver()
            device = rec.device_id
            if device.population != rec.from_population:
                raise UserError(
                    "%s has moved to %s since %s was requested; reject it and request again."
                    % (device.display_name, device._population_label(), rec.name)
                )
            if device.state == "scrapped":
                raise UserError("%s is scrapped." % device.display_name)
            if rec.from_population in COMPANY_POPULATIONS and rec.to_population == "customer_owned":
                rec._check_ownership_evidence(device, rec.ownership_id.id, exclude=rec)
            rec._guarded().write(
                {
                    "state": "applied",
                    "approved_by_id": self.env.uid,
                    "approved_at": fields.Datetime.now(),
                }
            )
            rec._apply()
        return True

    def action_reject(self, reason=None):
        if not (reason or "").strip():
            raise UserError("Say why the population change is rejected.")
        for rec in self:
            if rec.state != "requested":
                raise UserError("%s is not awaiting approval." % rec.name)
            rec._assert_approver()
            rec._guarded().write(
                {
                    "state": "rejected",
                    "approved_by_id": self.env.uid,
                    "approved_at": fields.Datetime.now(),
                    "decision_note": reason.strip(),
                }
            )
            rec.device_id.message_post(
                body="Population change %s rejected by %s: %s"
                % (rec.name, self.env.user.name, reason.strip())
            )
        return True

    def _check_ownership_evidence(self, device, ownership_id, exclude=None):
        ownership = self.env["fix.device.ownership"].sudo().browse(ownership_id or 0).exists()
        if not ownership:
            raise UserError(
                "%s is %s, 1000FiX's stock. It becomes customer-owned only with the ownership "
                "transfer that sold or gave it (BRU-AST-11): choose that transfer."
                % (device.display_name, device._population_label())
            )
        if ownership.device_id != device:
            raise UserError(
                "Ownership transfer %s is about another device." % ownership.display_name
            )
        # both are transaction timestamps, so a transfer recorded in the same
        # transaction as the change that brought the device in is not "earlier"
        last = self.sudo().search(
            [
                ("device_id", "=", device.id),
                ("state", "=", "applied"),
                ("id", "not in", (exclude or self.browse()).ids),
            ],
            order="create_date desc, id desc",
            limit=1,
        )
        if last and ownership.create_date and ownership.create_date < last.create_date:
            raise UserError(
                "Ownership transfer %s predates the device's last population change; it does not "
                "show the device leaving 1000FiX's stock." % ownership.display_name
            )
        used = self.sudo().search(
            [
                ("ownership_id", "=", ownership.id),
                ("state", "!=", "rejected"),
                ("id", "not in", (exclude or self.browse()).ids),
            ],
            limit=1,
        )
        if used:
            raise UserError(
                "Ownership transfer %s already supports population change %s."
                % (ownership.display_name, used.name)
            )


# =============================================================================
# p7 · BRU-AST-16 warranty derivation basis
# =============================================================================
class FixWarrantyBasis(models.Model):
    _inherit = "fix.warranty"

    derivation_basis = fields.Selection(
        WARRANTY_BASES,
        string="Dates Derived From",
        tracking=True,
        help="BRU-AST-16: how the start and end dates were established. A date defaulted "
        "from manufacture is flagged and cannot alone support a claim.",
    )
    basis_flag = fields.Char(string="Basis Flag", compute="_compute_basis_flag")

    @api.depends("derivation_basis")
    def _compute_basis_flag(self):
        for rec in self:
            if rec.derivation_basis == "manufacture_default":
                rec.basis_flag = "Defaulted dates: not claim support on their own"
            elif not rec.derivation_basis:
                rec.basis_flag = "Basis not recorded"
            else:
                rec.basis_flag = False

    @api.depends("verification_state", "proof_document_id", "status", "derivation_basis")
    def _compute_verification_blocker(self):
        super()._compute_verification_blocker()
        for rec in self:
            if rec.verification_blocker and rec.derivation_basis == "manufacture_default":
                rec.verification_blocker = (
                    "Dates are defaulted from manufacture: record the purchase evidence or brand "
                    "lookup that confirms them"
                )

    def _a07_verify_checks(self):
        for rec in self:
            if rec.warranty_type != "none" and rec.derivation_basis == "manufacture_default":
                raise UserError(
                    "The warranty on %s has dates defaulted from manufacture. A defaulted date "
                    "cannot alone support a claim (BRU-AST-16): change the basis to the purchase "
                    "evidence or brand lookup that confirms the dates, then request verification."
                    % rec.device_id.display_name
                )
        return super()._a07_verify_checks()


# =============================================================================
# p8 · FR-AST-038 estate structure and dated placements
# =============================================================================
NODE_TYPES = [("site", "Site"), ("department", "Department"), ("user", "Assigned User")]
# the level a node of each type hangs from
NODE_PARENT = {"site": (), "department": ("site",), "user": ("site", "department")}


class FixDeviceEstateNode(models.Model):
    _name = "fix.device.estate.node"
    _description = "Corporate Estate Node"
    _order = "estate_id, complete_name, id"
    _rec_name = "complete_name"

    name = fields.Char(string="Name", required=True)
    complete_name = fields.Char(
        string="Node", compute="_compute_complete_name", store=True, recursive=True
    )
    estate_id = fields.Many2one(
        "fix.device.estate", string="Estate", required=True, ondelete="cascade", index=True
    )
    client_id = fields.Many2one(related="estate_id.client_id", store=True, string="Client")
    parent_id = fields.Many2one(
        "fix.device.estate.node",
        string="Within",
        ondelete="restrict",
        index=True,
        domain="[('estate_id', '=', estate_id)]",
    )
    node_type = fields.Selection(NODE_TYPES, string="Level", required=True, default="site")
    contact_id = fields.Many2one(
        "res.partner",
        string="Contact / Assigned User",
        help="For a user node, the client's employee who holds the devices.",
    )
    address = fields.Char(string="Address")
    cost_centre = fields.Char(string="Cost Centre")
    active = fields.Boolean(default=True)
    device_count = fields.Integer(string="Devices", compute="_compute_device_count")

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        for rec in self:
            rec.complete_name = (
                "%s / %s" % (rec.parent_id.complete_name, rec.name) if rec.parent_id else rec.name
            )

    def _compute_device_count(self):
        groups = (
            self.env["fix.device"]
            .sudo()
            ._read_group([("estate_node_id", "in", self.ids)], ["estate_node_id"], ["__count"])
        )
        counts = {node.id: count for node, count in groups}
        for rec in self:
            rec.device_count = counts.get(rec.id, 0)

    @api.constrains("parent_id", "node_type", "estate_id", "contact_id")
    def _check_structure(self):
        for rec in self:
            allowed = NODE_PARENT[rec.node_type]
            if not allowed and rec.parent_id:
                raise ValidationError("A site is the top of the estate; it sits within nothing.")
            if allowed and not rec.parent_id:
                raise ValidationError(
                    "A %s sits within a %s of the estate."
                    % (dict(NODE_TYPES)[rec.node_type].lower(), " or ".join(allowed))
                )
            if rec.parent_id and rec.parent_id.estate_id != rec.estate_id:
                raise ValidationError("%s is in another estate." % rec.parent_id.complete_name)
            if rec.parent_id and rec.parent_id.node_type not in allowed:
                raise ValidationError(
                    "A %s cannot sit within a %s."
                    % (
                        dict(NODE_TYPES)[rec.node_type].lower(),
                        dict(NODE_TYPES)[rec.parent_id.node_type].lower(),
                    )
                )
            if rec.node_type == "user" and not rec.contact_id:
                raise ValidationError(
                    "Name the client's employee who holds the devices of %s." % rec.name
                )
            if (
                rec.contact_id
                and rec.contact_id.commercial_partner_id
                != rec.estate_id.client_id.commercial_partner_id
            ):
                raise ValidationError(
                    "%s is not a contact of %s."
                    % (rec.contact_id.name, rec.estate_id.client_id.name)
                )

    def write(self, vals):
        moving = "estate_id" in vals and any(rec.estate_id.id != vals["estate_id"] for rec in self)
        if moving and self.env["fix.device"].sudo().search_count(
            [("estate_node_id", "in", self.ids)]
        ):
            raise UserError("Devices are placed at this node; it does not move to another estate.")
        return super().write(vals)


class FixDeviceEstatePlacement(models.Model):
    """An asset at an estate node over time (FR-AST-038). Recording one moves
    the device; the previous placement is closed with the same date."""

    _name = "fix.device.estate.placement"
    _description = "Estate Placement"
    _inherit = ["fix.device.permanent.mixin"]
    _order = "placed_from desc, id desc"
    _permanent_hint = "A move is recorded as a new placement, which closes this one."

    name = fields.Char(string="Reference", required=True, default="New", copy=False)
    device_id = fields.Many2one(
        "fix.device", string="Device", required=True, ondelete="cascade", index=True
    )
    estate_id = fields.Many2one(
        "fix.device.estate", string="Estate", required=True, ondelete="restrict", index=True
    )
    node_id = fields.Many2one(
        "fix.device.estate.node",
        string="Node",
        ondelete="restrict",
        index=True,
        domain="[('estate_id', '=', estate_id)]",
    )
    placed_from = fields.Date(
        string="Placed From", required=True, default=fields.Date.context_today
    )
    placed_to = fields.Date(string="Placed To", readonly=True, copy=False)
    is_current = fields.Boolean(string="Current", default=True, readonly=True, index=True)
    move_reason = fields.Char(string="Reason for the Move", required=True)
    moved_by_id = fields.Many2one(
        "res.users", string="Recorded By", readonly=True, default=lambda self: self.env.uid
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"placed_to", "is_current", "moved_by_id"}

    def _close(self, on_date):
        for rec in self:
            rec._guarded().write({"is_current": False, "placed_to": max(on_date, rec.placed_from)})

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.context.get("fix_from_placement"):
            for vals in vals_list:
                if vals.get("name", "New") in (False, "", "New"):
                    vals["name"] = _seq(self.env, "fix.device.estate.placement", "DPLC/New")
            return super().create(vals_list)
        trusted = self._fix_guard_open()
        records = self.browse()
        for vals in vals_list:
            device = self.env["fix.device"].browse(vals.get("device_id") or 0).exists()
            estate = self.env["fix.device.estate"].browse(vals.get("estate_id") or 0).exists()
            node = self.env["fix.device.estate.node"].browse(vals.get("node_id") or 0).exists()
            if not device or not estate:
                raise UserError("Choose the device and the estate it is placed in.")
            if not trusted:
                device.check_access("write")
                if device.state in NOT_SCRAPPABLE:
                    raise UserError(
                        "%s is %s and is not placed anywhere."
                        % (device.display_name, device._state_label())
                    )
                if not device._owner_is(estate.client_id):
                    raise UserError(
                        "%s belongs to %s, not to %s, so it cannot be placed in the estate %s."
                        % (
                            device.display_name,
                            device.owner_id.name or "nobody",
                            estate.client_id.name,
                            estate.name,
                        )
                    )
            if node and node.estate_id != estate:
                raise UserError(
                    "%s is not a node of the estate %s." % (node.complete_name, estate.name)
                )
            if not node and self.env["fix.device.estate.node"].sudo().search_count(
                [("estate_id", "=", estate.id)]
            ):
                raise UserError(
                    "The estate %s is organised by site, department and user: place the device at "
                    "one of its nodes." % estate.name
                )
            current = self.sudo().search([("device_id", "=", device.id), ("is_current", "=", True)])
            placed_from = fields.Date.to_date(vals.get("placed_from")) or fields.Date.context_today(
                self
            )
            if current and current.estate_id == estate and current.node_id == node:
                raise UserError("%s is already placed there." % device.display_name)
            for old in current:
                if old.placed_from > placed_from:
                    raise UserError(
                        "%s has been placed at %s since %s; a move cannot be dated earlier (%s)."
                        % (
                            device.display_name,
                            old.node_id.complete_name or old.estate_id.name,
                            old.placed_from,
                            placed_from,
                        )
                    )
            if vals.get("name", "New") in (False, "", "New"):
                vals["name"] = _seq(self.env, "fix.device.estate.placement", "DPLC/New")
            rec = super().create([vals])
            _not_future(rec, rec.placed_from, "The placement date")
            current._close(rec.placed_from)
            device.sudo()._guarded().with_context(fix_from_placement=True).write(
                {"estate_id": estate.id, "estate_node_id": node.id or False}
            )
            device.message_post(
                body="Placed at %s (%s) from %s by %s: %s"
                % (
                    node.complete_name or estate.name,
                    estate.name,
                    rec.placed_from,
                    self.env.user.name,
                    rec.move_reason,
                )
            )
            records |= rec
        return records


# =============================================================================
# p10 · FR-AST-048 end-of-life routing decision (BRU-AST-19)
# =============================================================================
class FixDeviceEolDecision(models.Model):
    _name = "fix.device.eol.decision"
    _description = "End-of-Life Decision"
    _inherit = ["fix.guarded.mixin", "mail.thread"]
    _order = "id desc"

    name = fields.Char(string="Reference", required=True, default="New", copy=False)
    device_id = fields.Many2one(
        "fix.device", string="Device", required=True, ondelete="cascade", index=True
    )
    population = fields.Selection(related="device_id.population", string="Population")
    owner_id = fields.Many2one(related="device_id.owner_id", string="Owner")
    route = fields.Selection(EOL_ROUTES, string="Route", required=True)
    basis = fields.Text(string="Basis for the Decision", required=True)
    customer_instruction = fields.Selection(
        [
            ("refurbish", "Customer agreed: refurbish and resell (M14)"),
            ("recycle", "Customer agreed: recycle / dispose (M18)"),
            ("return_as_is", "Customer takes it back unrepaired"),
        ],
        string="Customer Instruction",
        help="Required for a customer-owned device (BRU-AST-19), and must match the route.",
    )
    instruction_reference = fields.Char(
        string="Instruction Reference", help="Signed form, call record or message that carries it."
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("requested", "Awaiting Approval"),
            ("approved", "Approved: Routed"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        required=True,
        readonly=True,
        index=True,
        tracking=True,
    )
    requested_by_id = fields.Many2one("res.users", string="Requested By", readonly=True, copy=False)
    requested_at = fields.Datetime(string="Requested At", readonly=True, copy=False)
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True, copy=False)
    decided_at = fields.Datetime(string="Decided At", readonly=True, copy=False)
    decision_note = fields.Char(string="Decision Note", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "requested_by_id",
            "requested_at",
            "decided_by_id",
            "decided_at",
            "decision_note",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id and self.state != "draft":
            locked |= {
                "device_id",
                "route",
                "basis",
                "customer_instruction",
                "instruction_reference",
            }
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") in (False, "", "New"):
                vals["name"] = _seq(self.env, "fix.device.eol.decision", "DEOL/New")
        records = super().create(vals_list)
        if not self._fix_guard_open():
            records._check_open_decision()
        return records

    def write(self, vals):
        if not self._fix_guard_open():
            for rec in self:
                if rec.state != "draft" and _changed(rec, vals):
                    raise UserError("%s is %s and is no longer edited." % (rec.name, rec.state))
        return super().write(vals)

    def unlink(self):
        if not self._fix_guard_open() and any(rec.state != "draft" for rec in self):
            raise UserError("A requested or decided end-of-life decision stays on record.")
        return super().unlink()

    def _check_open_decision(self):
        for rec in self:
            other = self.sudo().search(
                [
                    ("device_id", "=", rec.device_id.id),
                    ("state", "in", ("draft", "requested")),
                    ("id", "!=", rec.id),
                ],
                limit=1,
            )
            if other:
                raise UserError(
                    "%s already has an open end-of-life decision (%s)."
                    % (rec.device_id.display_name, other.name)
                )

    def _customer_owned(self):
        self.ensure_one()
        return self.device_id.population in ("customer_owned", "company_issued")

    def _check_instruction(self):
        for rec in self:
            if not rec._customer_owned():
                continue
            if not rec.customer_instruction:
                raise UserError(
                    "%s is customer-owned: record the customer's instruction before the decision "
                    "is requested (BRU-AST-19)." % rec.device_id.display_name
                )
            if rec.customer_instruction != EOL_INSTRUCTION_FOR_ROUTE[rec.route]:
                raise UserError(
                    "The customer's instruction (%s) does not allow the route %s."
                    % (
                        dict(rec._fields["customer_instruction"].selection)[
                            rec.customer_instruction
                        ],
                        dict(EOL_ROUTES)[rec.route],
                    )
                )

    def action_request(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is already %s." % (rec.name, rec.state))
            rec.device_id.check_access("write")
            if rec.device_id.state in NOT_SCRAPPABLE:
                raise UserError(
                    "%s is %s: no end-of-life route is decided for it."
                    % (rec.device_id.display_name, rec.device_id._state_label())
                )
            rec._check_instruction()
            rec._guarded().write(
                {
                    "state": "requested",
                    "requested_by_id": self.env.uid,
                    "requested_at": fields.Datetime.now(),
                }
            )
        return True

    def _assert_approver(self):
        self.ensure_one()
        self.device_id._assert_role(BRANCH_MANAGER_GROUP, "Deciding an end-of-life route")
        if self.env.uid in (self.requested_by_id.id, self.create_uid.id) and not self.env.su:
            raise UserError(
                "Segregation of duties: the person who raised or requested %s cannot decide it."
                % self.name
            )

    def action_approve(self):
        for rec in self:
            if rec.state != "requested":
                raise UserError("%s is not awaiting approval." % rec.name)
            rec._assert_approver()
            rec._check_instruction()
            rec._guarded().write(
                {
                    "state": "approved",
                    "decided_by_id": self.env.uid,
                    "decided_at": fields.Datetime.now(),
                }
            )
            rec._route()
        return True

    def action_reject(self, reason=None):
        if not (reason or "").strip():
            raise UserError("Say why the route is rejected.")
        for rec in self:
            if rec.state != "requested":
                raise UserError("%s is not awaiting approval." % rec.name)
            rec._assert_approver()
            rec._guarded().write(
                {
                    "state": "rejected",
                    "decided_by_id": self.env.uid,
                    "decided_at": fields.Datetime.now(),
                    "decision_note": reason.strip(),
                }
            )
        return True

    def _route(self):
        """Apply the approved route on the device: the lifecycle stage and the
        population that hands it to M14 or M18 (FR-AST-048)."""
        self.ensure_one()
        device = self.device_id.sudo()
        vals = {
            "lifecycle_decided_by_id": self.decided_by_id.id,
            "lifecycle_decided_at": self.decided_at,
            "lifecycle_reason": "%s: %s" % (self.name, self.basis),
        }
        if self.route in ("refurbish", "dispose"):
            vals["lifecycle_stage"] = "obsolete"
            vals["end_of_support_date"] = device.end_of_support_date or fields.Date.context_today(
                self
            )
        if self.customer_instruction:
            vals["eol_customer_instruction"] = self.customer_instruction
        device._guarded().write(vals)
        target = {
            "refurbish": "trade_in_intake" if self._customer_owned() else "refurbishment_stock",
            "dispose": "ewaste_pending",
        }.get(self.route)
        if target and device.population != target:
            self.env["fix.device.population.change"].sudo()._guarded().create(
                {
                    "device_id": device.id,
                    "to_population": target,
                    "reason_code": "eol_decision",
                    "notes": "%s approved by %s" % (self.name, self.decided_by_id.name),
                }
            )
        device.add_history(
            "other",
            "End-of-life decision %s: %s, approved by %s. Basis: %s"
            % (self.name, dict(EOL_ROUTES)[self.route], self.decided_by_id.name, self.basis),
        )
        # A07 ERP audit M17-10 / AUT-AST-17: the route was a label. M14 / M18
        # are told (device.end_of_life), and a refurbish or dispose route closes
        # the device's open plans and 1000FiX entitlements.
        if self.route in ("refurbish", "dispose"):
            device._a07_close_for_end_of_life(
                "end-of-life decision %s (%s)" % (self.name, dict(EOL_ROUTES)[self.route]),
                route=self.route,
                decision=self,
            )


# =============================================================================
# p11 · FR-AST-051 stewardship worklist (BRU-AST-22)
# =============================================================================
class FixDeviceQualityIssue(models.Model):
    _name = "fix.device.quality.issue"
    _description = "Device Stewardship Issue"
    _inherit = ["fix.guarded.mixin", "mail.thread", "mail.activity.mixin"]
    _order = "escalated desc, severity_rank, raised_at, id"

    name = fields.Char(string="Reference", required=True, default="New", copy=False)
    device_id = fields.Many2one(
        "fix.device", string="Device", required=True, ondelete="cascade", index=True
    )
    issue_type = fields.Selection(
        [
            ("provisional", "Provisional identity"),
            ("duplicate", "Probable duplicate"),
            ("conflict", "Identifier conflict"),
            ("incomplete", "Incomplete record"),
        ],
        string="Issue",
        required=True,
    )
    severity = fields.Selection(
        [("high", "High"), ("medium", "Medium"), ("low", "Low")],
        string="Severity",
        required=True,
        default="medium",
    )
    severity_rank = fields.Integer(compute="_compute_severity_rank", store=True)
    description = fields.Text(string="What Is Wrong", required=True)
    assigned_branch_id = fields.Many2one("fix.branch", string="Assigned Branch", index=True)
    assigned_to_id = fields.Many2one("res.users", string="Assigned To", index=True)
    raised_by_id = fields.Many2one(
        "res.users", string="Raised By", readonly=True, default=lambda self: self.env.uid
    )
    raised_at = fields.Datetime(string="Raised At", readonly=True, default=fields.Datetime.now)
    age_days = fields.Integer(string="Age (days)", compute="_compute_age_days")
    state = fields.Selection(
        [("open", "Open"), ("in_progress", "In Progress"), ("resolved", "Resolved")],
        default="open",
        required=True,
        readonly=True,
        index=True,
        tracking=True,
    )
    escalated = fields.Boolean(string="Escalated", readonly=True, copy=False, index=True)
    escalated_at = fields.Datetime(string="Escalated At", readonly=True, copy=False)
    resolution = fields.Text(string="Resolution", readonly=True, copy=False)
    resolved_by_id = fields.Many2one("res.users", string="Resolved By", readonly=True, copy=False)
    resolved_at = fields.Datetime(string="Resolved At", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        # A07 ERP audit M17-12: a clerk wrote himself in as the assignee and then
        # resolved an identifier conflict he caused. A Branch Manager assigns.
        return super()._fix_guarded_fields() | {
            "state",
            "escalated",
            "escalated_at",
            "resolution",
            "resolved_by_id",
            "resolved_at",
            "raised_by_id",
            "raised_at",
            "assigned_to_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id:
            locked |= {"device_id", "issue_type"}
            if self.state == "resolved":
                locked |= {"severity", "description", "assigned_branch_id", "assigned_to_id"}
        return locked

    @api.depends("severity")
    def _compute_severity_rank(self):
        rank = {"high": 0, "medium": 1, "low": 2}
        for rec in self:
            rec.severity_rank = rank.get(rec.severity, 1)

    def _compute_age_days(self):
        now = fields.Datetime.now()
        for rec in self:
            end = rec.resolved_at or now
            rec.age_days = (end - rec.raised_at).days if rec.raised_at else 0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") in (False, "", "New"):
                vals["name"] = _seq(self.env, "fix.device.quality.issue", "DDQ/New")
            if not vals.get("assigned_branch_id") and vals.get("device_id"):
                device = self.env["fix.device"].sudo().browse(vals["device_id"]).exists()
                vals["assigned_branch_id"] = device.branch_id.id or False
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open():
            for rec in self:
                if rec.state == "resolved" and _changed(rec, vals):
                    raise UserError("%s is resolved and stays as it was resolved." % rec.name)
                if "device_id" in vals and rec._fix_guard_differs(
                    "device_id", vals["device_id"], rec.device_id
                ):
                    raise UserError("An issue stays on the device it was raised for.")
        return super().write(vals)

    def unlink(self):
        if not self._fix_guard_open():
            raise UserError("A stewardship issue stays on record; resolve it instead.")
        return super().unlink()

    def _assert_steward(self):
        self.ensure_one()
        if self.env.su or self.env.uid == self.assigned_to_id.id:
            return
        if self.issue_type in QM_ISSUE_TYPES and self.env.user.has_group(QUALITY_MANAGER_GROUP):
            # BRU-AST-05: conflicts and duplicates are the Quality Manager's.
            return
        self.device_id._assert_role(
            BRANCH_MANAGER_GROUP, "Working an issue assigned to someone else"
        )

    def action_assign(self, user_id=None):
        """A Branch Manager assigns the issue to a steward (M17-12)."""
        Users = self.env["res.users"].sudo()
        text = str(user_id or "").strip()
        user = (
            Users.browse(int(text)).exists()
            if text.isdigit()
            else Users.search([("login", "=", text)], limit=1)
        )
        if not user or not user._is_internal():
            raise UserError("Choose the internal user who works the issue.")
        for rec in self:
            if rec.state == "resolved":
                raise UserError("%s is resolved." % rec.name)
            rec.device_id._assert_role(BRANCH_MANAGER_GROUP, "Assigning a stewardship issue")
            rec._guarded().write({"assigned_to_id": user.id})
            rec.message_post(body="Assigned to %s by %s." % (user.name, self.env.user.name))
        return True

    def action_start(self):
        for rec in self:
            if rec.state != "open":
                raise UserError("%s is not open." % rec.name)
            rec._assert_steward()
            rec._guarded().write({"state": "in_progress"})
        return True

    def action_resolve(self, resolution=None):
        if not (resolution or "").strip():
            raise UserError("Say how the record was put right.")
        for rec in self:
            if rec.state == "resolved":
                raise UserError("%s is already resolved." % rec.name)
            rec._assert_steward()
            if rec.issue_type in QM_ISSUE_TYPES:
                # BRU-AST-05: a conflict or duplicate is the Quality Manager's.
                rec.device_id._assert_role(
                    QUALITY_MANAGER_GROUP, "Resolving an identifier conflict or duplicate"
                )
                if not self.env.su and self.env.user == rec.raised_by_id:
                    raise UserError(
                        "Segregation of duties: you raised %s, so another Quality Manager "
                        "resolves it." % rec.name
                    )
            if rec.issue_type == "provisional" and rec.device_id.state == "provisional":
                raise UserError(
                    "%s is still provisional: capture its identifier and confirm the identity "
                    "first." % rec.device_id.display_name
                )
            rec._guarded().write(
                {
                    "state": "resolved",
                    "resolution": resolution.strip(),
                    "resolved_by_id": self.env.uid,
                    "resolved_at": fields.Datetime.now(),
                }
            )
            if rec.issue_type == "conflict":
                rec.device_id.sudo()._a07_release_quarantine()
        return True

    def _escalation_users(self):
        """Who an escalation reaches: the branch's manager, else the device
        branch managers of the device's company (M17-30)."""
        self.ensure_one()
        branch = self.assigned_branch_id.sudo()
        users = self.env["res.users"]
        manager = branch.manager_id if "manager_id" in branch._fields else users
        if manager and manager._name == "res.users":
            users |= manager
        elif manager and manager._name == "hr.employee":
            users |= manager.user_id
        if not users:
            group = self.env.ref(BRANCH_MANAGER_GROUP, raise_if_not_found=False)
            company = self.device_id.sudo().company_id
            if group:
                users = group.sudo().all_user_ids.filtered(
                    lambda u: company in u.company_ids and not u._is_superuser()
                )
        return users.filtered(lambda u: u.active and u._is_internal())

    @api.model
    def cron_steward_sweep(self):
        """BRU-AST-22: a provisional identity older than the threshold goes on
        the worklist; an issue open beyond the escalation threshold escalates
        to the branch's managers. Idempotent."""
        env = self.sudo().env
        Issue = env["fix.device.quality.issue"]._guarded()
        now = fields.Datetime.now()
        provisional_days = _int_param(
            env, STEWARD_PROVISIONAL_DAYS_PARAM, STEWARD_PROVISIONAL_DAYS_DEFAULT
        )
        escalation_days = _int_param(
            env, STEWARD_ESCALATION_DAYS_PARAM, STEWARD_ESCALATION_DAYS_DEFAULT
        )
        stale = env["fix.device"].search(
            [
                ("state", "=", "provisional"),
                ("create_date", "<", now - timedelta(days=provisional_days)),
            ]
        )
        listed = set(
            Issue.search(
                [
                    ("device_id", "in", stale.ids),
                    ("issue_type", "=", "provisional"),
                    ("state", "!=", "resolved"),
                ]
            ).device_id.ids
        )
        for device in stale.filtered(lambda d: d.id not in listed):
            Issue.create(
                {
                    "device_id": device.id,
                    "issue_type": "provisional",
                    "severity": "medium",
                    "description": "Provisional identity unresolved for more than %d days: %s"
                    % (provisional_days, device.provisional_reason or "no reason recorded"),
                }
            )
        overdue = Issue.search(
            [
                ("state", "!=", "resolved"),
                ("escalated", "=", False),
                ("raised_at", "<", now - timedelta(days=escalation_days)),
            ]
        )
        for issue in overdue:
            issue.write({"escalated": True, "escalated_at": now})
            issue.message_post(
                body="Escalated to the Branch Manager: open for more than %d days."
                % escalation_days
            )
            # M17-30: chatter alone reached nobody; the manager gets an activity.
            for user in issue._escalation_users()[:3]:
                issue.activity_schedule(
                    "mail.mail_activity_data_todo",
                    user_id=user.id,
                    summary="Stewardship issue %s escalated" % issue.name,
                    note="%s on %s has been open for more than %d days: %s"
                    % (
                        issue.name,
                        issue.device_id.display_name,
                        escalation_days,
                        issue.description,
                    ),
                )
        return True
