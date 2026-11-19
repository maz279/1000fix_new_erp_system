# M37 capture audit, third pass (2026-11-19). Every page had a "+ New" after
# the first two passes, but several opened a form that could not hold what the
# spec (§5, §10.1) says the page records:
#
# - Service Definition (FR-CAT-013..019): the service form had a name, a type
#   and a labour time - no scope of work, inclusions, exclusions,
#   prerequisites, deliverables, delivery modes, standard duration per mode,
#   repair warranty or consent / compliance flags.
# - Repair Operations (FR-CAT-026): no tooling or workstation requirement.
# - Part Identity (FR-CAT-029): the part form showed no manufacturer part
#   number or OEM reference.
# - Product Hierarchy & Variants (FR-CAT-004/005): no attribute sets per item
#   class, and no commercial vs presentation tree.
# - Brand-Model-Device (FR-CAT-033, BRU-CAT-07): no compatibility matrix, so
#   nothing stopped an rBOM line naming a part that does not fit the model.
# - Contract & Protection Templates (FR-CAT-038): no subscription plan
#   definition anywhere.
#
# File name sorts after fix_catalogue_spec_records (ruff I001 re-sorts the
# imports in models/__init__.py; these models point at the item).
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .catalogue_roles import ROLE_OFFICER, require_role
from .fix_catalogue_item import ITEM_STATES

# FR-CAT-014: the nine delivery modes.
DELIVERY_MODES = [
    ("walk_in", "Walk-in (service centre counter)"),
    ("on_site", "On-site (technician visit)"),
    ("pick_drop", "Pick & drop"),
    ("workshop", "Workshop / depot"),
    ("remote", "Remote"),
    ("managed", "Managed service"),
    ("rental_service", "Rental service"),
    ("data_service", "Data service"),
    ("marketplace", "Marketplace"),
]
# The item types a technician performs: they carry a scope of work and a
# standard duration per delivery mode before they may leave Draft.
SERVICE_TYPES = ("service", "inspection", "labour")
WORKSTATION_CLASSES = [
    ("standard_bench", "Standard bench"),
    ("esd_bench", "ESD-safe bench"),
    ("micro_soldering", "Micro-soldering / BGA station"),
    ("clean_room", "Clean room / dust-free (displays, drives)"),
    ("refrigerant", "Refrigerant recovery station"),
    ("field_kit", "Field kit (on-site)"),
]
# BRU-CAT-12: the scope of an Active service is what was approved. A blank
# one (every migrated item) may be completed; a set one changes only by
# Revise and re-approval.
SCOPE_ONCE_SET = frozenset({"scope_of_work", "inclusions", "exclusions"})
TREE_TYPES = [
    ("commercial", "Commercial tree (the one items are approved under)"),
    ("presentation", "Presentation tree (website / app navigation)"),
]
CHANNEL_REQUIREMENT = [
    ("all", "Every item of the class (before review)"),
    ("portal", "Customer portal / website"),
    ("app", "Customer mobile app"),
    ("corporate", "Corporate (B2B) portal"),
    ("marketplace", "Marketplace"),
    ("print", "Printed catalogue"),
    ("pos", "Counter / POS"),
]
BILLING_FREQUENCIES = [
    ("monthly", "Monthly"),
    ("quarterly", "Quarterly"),
    ("half_yearly", "Half-yearly"),
    ("yearly", "Yearly"),
]


class FixServiceModeDuration(models.Model):
    """FR-CAT-014/016: a delivery mode the service supports, with its
    standard duration in that mode. A service supports exactly the modes it
    has a line for."""

    _name = "fix.service.mode.duration"
    _description = "Service Delivery Mode & Standard Duration"
    _order = "item_id, delivery_mode"

    item_id = fields.Many2one(
        "fix.catalogue.item",
        string="Service",
        required=True,
        index=True,
        ondelete="cascade",
    )
    delivery_mode = fields.Selection(DELIVERY_MODES, string="Delivery Mode", required=True)
    standard_minutes = fields.Float(
        string="Standard Duration (minutes)",
        required=True,
        help="Appointment sizing, capacity planning and the SLA start from it.",
    )
    note = fields.Char(string="Mode Note")

    _unique_mode = models.Constraint(
        "UNIQUE (item_id, delivery_mode)",
        "A service states each delivery mode once.",
    )

    @api.constrains("standard_minutes")
    def _check_minutes(self):
        for rec in self:
            if not rec.standard_minutes or rec.standard_minutes <= 0:
                raise ValidationError(
                    "A delivery mode needs a positive standard duration (FR-CAT-016)."
                )

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, (ROLE_OFFICER,), "Changing a service's delivery modes")
        return super().create(vals_list)

    def write(self, vals):
        require_role(self.env, (ROLE_OFFICER,), "Changing a service's delivery modes")
        return super().write(vals)

    def unlink(self):
        require_role(self.env, (ROLE_OFFICER,), "Changing a service's delivery modes")
        return super().unlink()


class FixModelCompatibility(models.Model):
    """FR-CAT-033: whether a part or an operation applies to a device model.
    A row saying "not compatible" blocks the part on an rBOM line for that
    model (BRU-CAT-07)."""

    _name = "fix.model.compatibility"
    _description = "Model Compatibility (part / operation <-> model)"
    _order = "device_model_id, item_id"
    _rec_name = "display_label"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    device_model_id = fields.Many2one(
        "fix.device.model", string="Device Model", required=True, index=True, ondelete="restrict"
    )
    brand_id = fields.Many2one(related="device_model_id.brand_id", store=True, string="Brand")
    item_id = fields.Many2one(
        "fix.catalogue.item",
        string="Part / Operation",
        required=True,
        index=True,
        ondelete="restrict",
        domain=[("item_type", "in", ["part", "accessory", "labour", "service", "inspection"])],
    )
    item_type = fields.Selection(related="item_id.item_type", string="Item Type")
    compatible = fields.Boolean(
        string="Compatible",
        default=True,
        help="Off: the part or operation does NOT apply to this model and is refused there.",
    )
    note = fields.Text(
        string="Fit Note",
        help="How it fits (revision, region, board version) or why it does not. Mandatory "
        "when not compatible.",
    )
    evidence_ref = fields.Char(string="Source (brand bulletin, parts catalogue page)")
    active = fields.Boolean(default=True)
    display_label = fields.Char(compute="_compute_display_label", store=True)

    @api.depends("device_model_id", "item_id", "compatible")
    def _compute_display_label(self):
        for rec in self:
            rec.display_label = "%s %s %s" % (
                rec.item_id.name or "?",
                "fits" if rec.compatible else "does NOT fit",
                rec.device_model_id.name or "?",
            )

    @api.constrains("device_model_id", "item_id", "compatible", "note", "active")
    def _check_row(self):
        for rec in self:
            if not rec.compatible and not (rec.note or "").strip():
                raise ValidationError(
                    "Say why %s does not fit %s (FR-CAT-033)."
                    % (rec.item_id.display_name, rec.device_model_id.display_name)
                )
            # one row per model and item (a SQL UNIQUE would also hold the
            # archived row; a Python check keeps history)
            twin = self.search_count(
                [
                    ("id", "!=", rec.id),
                    ("device_model_id", "=", rec.device_model_id.id),
                    ("item_id", "=", rec.item_id.id),
                ]
            )
            if rec.active and twin:
                raise ValidationError(
                    "%s already has a compatibility row for %s: change that one."
                    % (rec.item_id.display_name, rec.device_model_id.display_name)
                )
            if rec.active and not rec.compatible:
                Line = self.env["fix.rbom.line"].sudo()
                used = Line.search(
                    [
                        ("component_item_id", "=", rec.item_id.id),
                        "|",
                        ("device_model_id", "=", rec.device_model_id.id),
                        "&",
                        ("device_model_id", "=", False),
                        ("item_id.device_model_ids", "in", rec.device_model_id.ids),
                    ],
                    limit=1,
                )
                if used:
                    raise ValidationError(
                        "%s is on %s's rBOM for %s: take it off that rBOM before declaring "
                        "it incompatible (BRU-CAT-07)."
                        % (
                            rec.item_id.display_name,
                            used.item_id.name,
                            rec.device_model_id.display_name,
                        )
                    )

    @api.model
    def _incompatible(self, items, device_models):
        """The (item, model) pairs declared NOT compatible, for BRU-CAT-07."""
        if not items or not device_models:
            return self.browse()
        return self.sudo().search(
            [
                ("item_id", "in", items.ids),
                ("device_model_id", "in", device_models.ids),
                ("compatible", "=", False),
            ]
        )

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, (ROLE_OFFICER,), "Recording model compatibility")
        return super().create(vals_list)

    def write(self, vals):
        require_role(self.env, (ROLE_OFFICER,), "Changing model compatibility")
        return super().write(vals)

    def unlink(self):
        require_role(self.env, (ROLE_OFFICER,), "Deleting model compatibility")
        return super().unlink()


class FixCatalogueAttributeSet(models.Model):
    """FR-CAT-005: the attributes an item class must carry, which of them are
    mandatory before review, and which a channel requires."""

    _name = "fix.catalogue.attribute.set"
    _description = "Catalogue Attribute Set (per item class)"
    _inherit = ["mail.thread"]
    _order = "item_type, name"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, tracking=True)
    item_type = fields.Selection(
        selection=lambda self: self.env["fix.catalogue.item"]._fields["item_type"].selection,
        string="Item Class",
        required=True,
        index=True,
        tracking=True,
    )
    line_ids = fields.One2many(
        "fix.catalogue.attribute.set.line", "set_id", string="Attributes", copy=True
    )
    note = fields.Text()
    active = fields.Boolean(default=True, tracking=True)

    @api.constrains("item_type", "active")
    def _check_one_per_class(self):
        for rec in self.filtered("active"):
            if self.search_count(
                [("id", "!=", rec.id), ("item_type", "=", rec.item_type), ("active", "=", True)]
            ):
                raise ValidationError(
                    "The %s class already has an active attribute set: change that one."
                    % dict(self._fields["item_type"].selection(self)).get(rec.item_type)
                )

    @api.model
    def _for(self, item_type):
        return self.sudo().search([("item_type", "=", item_type)], limit=1)

    def _missing(self, item, channel="all"):
        """The attributes this set requires for `channel` that the item's
        product does not carry."""
        self.ensure_one()
        carried = item.product_tmpl_id.sudo().attribute_line_ids.mapped("attribute_id")
        lines = self.line_ids.filtered(
            lambda line: line.mandatory and line.channel in ("all", channel)
        )
        return lines.mapped("attribute_id") - carried

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, (ROLE_OFFICER,), "Defining an attribute set")
        return super().create(vals_list)

    def write(self, vals):
        require_role(self.env, (ROLE_OFFICER,), "Changing an attribute set")
        return super().write(vals)

    def unlink(self):
        raise UserError("An attribute set is archived, never deleted.")


class FixCatalogueAttributeSetLine(models.Model):
    _name = "fix.catalogue.attribute.set.line"
    _description = "Catalogue Attribute Set Line"
    _order = "set_id, sequence, id"

    set_id = fields.Many2one(
        "fix.catalogue.attribute.set", required=True, index=True, ondelete="cascade"
    )
    sequence = fields.Integer(default=10)
    attribute_id = fields.Many2one(
        "product.attribute", string="Attribute", required=True, ondelete="restrict"
    )
    mandatory = fields.Boolean(string="Mandatory", default=True)
    channel = fields.Selection(
        CHANNEL_REQUIREMENT,
        string="Required For",
        required=True,
        default="all",
        help="'Every item of the class': the item cannot leave Draft without it. A channel: "
        "the item is counted incomplete for that channel's publication.",
    )
    note = fields.Char()

    _unique_attribute = models.Constraint(
        "UNIQUE (set_id, attribute_id, channel)",
        "An attribute is listed once per channel in a set.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, (ROLE_OFFICER,), "Changing an attribute set")
        return super().create(vals_list)

    def write(self, vals):
        require_role(self.env, (ROLE_OFFICER,), "Changing an attribute set")
        return super().write(vals)

    def unlink(self):
        require_role(self.env, (ROLE_OFFICER,), "Changing an attribute set")
        return super().unlink()


class FixSubscriptionPlanDef(models.Model):
    """FR-CAT-038: a subscription plan definition - what M39 bills, never the
    price (M11 prices it; BRU-CAT-01)."""

    _name = "fix.subscription.plan.def"
    _description = "Subscription Plan Definition"
    _inherit = ["mail.thread"]
    _order = "item_id, id"
    _rec_name = "name"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    item_id = fields.Many2one(
        "fix.catalogue.item",
        string="Plan Item",
        required=True,
        index=True,
        ondelete="restrict",
        domain=[("item_type", "in", ["subscription", "protection", "service"])],
    )
    name = fields.Char(related="item_id.name", store=True, string="Plan")
    billing_frequency = fields.Selection(BILLING_FREQUENCIES, required=True, tracking=True)
    commitment_months = fields.Integer(
        string="Commitment Term (months)", required=True, default=12, tracking=True
    )
    included_quantity = fields.Float(
        string="Included Quantity per Period",
        help="E.g. 4 visits, 10 devices, 50 GB. Zero: unlimited within fair use.",
    )
    included_uom_id = fields.Many2one("uom.uom", string="Included Unit")
    overage_uom_id = fields.Many2one(
        "uom.uom",
        string="Overage Charged Per",
        help="The unit usage above the inclusion is billed in.",
    )
    entitlement_note = fields.Text(string="What the Plan Includes")
    active = fields.Boolean(default=True, tracking=True)

    @api.constrains("commitment_months", "included_quantity", "item_id")
    def _check_plan(self):
        for rec in self:
            if rec.commitment_months < 1:
                raise ValidationError("A plan commits for at least one month.")
            if rec.included_quantity < 0:
                raise ValidationError("An included quantity is never negative.")
            if self.search_count([("id", "!=", rec.id), ("item_id", "=", rec.item_id.id)]):
                raise ValidationError(
                    "%s already has a plan definition: change that one." % rec.item_id.display_name
                )

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, (ROLE_OFFICER,), "Defining a subscription plan")
        return super().create(vals_list)

    def write(self, vals):
        require_role(self.env, (ROLE_OFFICER,), "Changing a subscription plan")
        return super().write(vals)

    def unlink(self):
        raise UserError("A plan definition is archived, never deleted.")


class ProductCategory(models.Model):
    """FR-CAT-004: a category node is bilingual and coded, and belongs to the
    one commercial tree or to a presentation tree."""

    _inherit = "product.category"

    name_bn = fields.Char(string="Category Name (Bengali)")
    code = fields.Char(string="Category Code", index=True)
    tree_type = fields.Selection(
        TREE_TYPES,
        string="Tree",
        required=True,
        default="commercial",
        help="Items are approved under the commercial tree (BRU-CAT-02); presentation trees "
        "only arrange items for a website or app.",
    )

    @api.constrains("parent_id", "tree_type")
    def _check_tree_type(self):
        for rec in self:
            if rec.parent_id and rec.parent_id.tree_type != rec.tree_type:
                raise ValidationError(
                    "%s sits under %s, which is in the %s; a node stays in its parent's tree."
                    % (
                        rec.name,
                        rec.parent_id.complete_name,
                        dict(TREE_TYPES)[rec.parent_id.tree_type].split(" (")[0].lower(),
                    )
                )

    _unique_code = models.Constraint(
        "UNIQUE (code)",
        "Category codes are unique.",
    )


class FixCatalogueItemStructure(models.Model):
    _inherit = "fix.catalogue.item"

    # ---- FR-CAT-013: the service definition --------------------------------
    scope_of_work = fields.Text(string="Scope of Work", tracking=True)
    inclusions = fields.Text(string="Included", tracking=True)
    exclusions = fields.Text(string="Not Included", tracking=True)
    prerequisites = fields.Text(
        string="Prerequisites", help="What the customer or device must provide first."
    )
    deliverables = fields.Text(string="Deliverables")
    # ---- FR-CAT-014/016 ------------------------------------------------------
    mode_duration_ids = fields.One2many(
        "fix.service.mode.duration",
        "item_id",
        string="Delivery Modes & Standard Durations",
    )
    # ---- FR-CAT-018/019 ------------------------------------------------------
    repair_warranty_days = fields.Integer(
        string="Repair Warranty (days)",
        help="Default warranty on the work, given by M01 at handover.",
    )
    requires_customer_consent = fields.Boolean(string="Needs Explicit Customer Consent")
    requires_data_declaration = fields.Boolean(string="Needs a Data-Handling Declaration")
    requires_regulatory_cert = fields.Boolean(string="Needs a Regulatory Certification")
    # ---- FR-CAT-026 ----------------------------------------------------------
    tooling_required = fields.Text(string="Tools & Test Equipment")
    workstation_class = fields.Selection(WORKSTATION_CLASSES, string="Workstation Class")
    # ---- FR-CAT-029: the part's identity -------------------------------------
    # The MPN lives on the product (the inventory file's 'Principal Part No');
    # a Catalogue Officer may not write product templates, so write() routes it.
    manufacturer_part_number = fields.Char(
        related="product_tmpl_id.manufacturer_part_number",
        string="Manufacturer Part Number (MPN)",
        readonly=False,
    )
    oem_reference = fields.Char(
        string="OEM Reference", index=True, help="The brand's own reference for the part."
    )
    compatibility_ids = fields.One2many(
        "fix.model.compatibility", "item_id", string="Model Compatibility"
    )

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(rec.state != "draft" for rec in self):
            locked |= {n for n in SCOPE_ONCE_SET if any(rec[n] for rec in self)}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        mpns = [vals.pop("manufacturer_part_number", None) for vals in vals_list]
        records = super().create(vals_list)
        for rec, mpn in zip(records, mpns, strict=True):
            if mpn:
                rec.product_tmpl_id.sudo().manufacturer_part_number = mpn
        return records

    def write(self, vals):
        if not self._fix_guard_open():
            names = SCOPE_ONCE_SET & set(vals)
            for rec in self.filtered(lambda r: r.state != "draft"):
                moved = [n for n in names if rec[n] and rec._fix_guard_differs(n, vals[n], rec[n])]
                if moved:
                    raise UserError(
                        "%s is %s and its %s is what was approved (BRU-CAT-12). Revise the "
                        "item (back to Draft) and have the change approved."
                        % (
                            rec.display_name,
                            dict(ITEM_STATES)[rec.state],
                            ", ".join(self._fields[n].string.lower() for n in sorted(moved)),
                        )
                    )
            if "manufacturer_part_number" in vals:
                require_role(self.env, (ROLE_OFFICER,), "Changing a part number")
                vals = dict(vals)
                mpn = vals.pop("manufacturer_part_number")
                self.mapped("product_tmpl_id").sudo().write({"manufacturer_part_number": mpn})
                if not vals:
                    return True
        return super().write(vals)

    def _references(self):
        # The delivery-mode lines are part of the service (deleted with it),
        # not a document that refers to it: a draft service stays deletable
        # by its officer (BRU-CAT-03 is about references).
        return [r for r in super()._references() if r[0] != "fix.service.mode.duration"]

    def _completeness_problems(self):
        problems = super()._completeness_problems()
        if self.item_type in SERVICE_TYPES:
            if not (self.scope_of_work or "").strip():
                problems.append("its scope of work (FR-CAT-013)")
            if not self.mode_duration_ids:
                problems.append(
                    "at least one delivery mode with its standard duration (FR-CAT-014/016)"
                )
        if self.category_id and self.category_id.tree_type != "commercial":
            problems.append(
                "a place in the commercial tree: %s is a presentation category (BRU-CAT-02)"
                % self.category_id.complete_name
            )
        attr_set = self.env["fix.catalogue.attribute.set"]._for(self.item_type)
        if attr_set:
            missing = attr_set._missing(self)
            if missing:
                problems.append(
                    "the attributes its class requires: %s (FR-CAT-005)"
                    % ", ".join(missing.mapped("name"))
                )
        return problems
