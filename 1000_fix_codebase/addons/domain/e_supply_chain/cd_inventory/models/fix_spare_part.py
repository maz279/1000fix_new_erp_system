# cd_inventory — Spare Parts Master & Device Compatibility (M15, CD-M15-01).
from __future__ import annotations

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_inventory_approval import CONTROLLER_GROUP, COST_GROUP, VALUED_CLASSES


class FixSparePart(models.Model):
    """Spare parts master record with device compatibility and serialized tracking."""

    _name = "fix.spare.part"
    _description = "Spare Part & Component"
    # A06 audit (2026-11-03) M15-1/M15-6: qty_available and unit_cost were
    # free fields: a clerk typed stock to 9,999, created a part born with
    # 1,000 on hand and re-priced a part 500 -> 1 BDT. The on-hand and
    # reserved quantities are now the SUM of the location ledger
    # (fix.stock.onhand) and change only by a movement; the standard cost and
    # the part status change only by an Inventory Controller action.
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]

    company_id = fields.Many2one(
        "res.company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Operating Unit",
        index=True,
    )
    name = fields.Char(string="Part Description", required=True, tracking=True)
    name_bn = fields.Char(string="যন্ত্রাংশের নাম (বাংলা)", help="Bengali name per DoD-08")
    part_number = fields.Char(string="Part Number / SKU", required=True, index=True)
    barcode = fields.Char(string="Barcode (EAN-13 / UPC)", index=True)
    qr_code = fields.Char(string="Internal QR Code", index=True)
    sales_price = fields.Float(string="Retail Replacement Price (BDT)", default=0.0)

    part_category = fields.Selection(
        [
            ("display", "Display & Touch Screen Assembly"),
            ("battery", "Lithium Battery Pack"),
            ("motherboard", "Motherboard / Main PCB"),
            ("camera", "Front / Rear Camera Module"),
            ("charging_port", "Charging Port & Sub-PCB"),
            ("compressor", "Inverter / Rotary Compressor"),
            ("motor", "Drive Motor & Pump"),
            ("sensor", "Thermal / Pressure Sensor"),
            ("fastener", "Housing, Screws & Thermal Pads"),
        ],
        string="Component Category",
        required=True,
        default="display",
        tracking=True,
    )

    device_brand = fields.Char(string="Device Brand / Manufacturer", index=True)
    category = fields.Selection(related="part_category", string="Category", store=True)
    brand = fields.Char(related="device_brand", string="Brand", store=True)

    # Real-inventory fit-gap (2026-11-07, report §7 R2): the real inventory
    # statement classifies every row as Group -> Category (41 groups, 455
    # category names) under a governed brand. The 9-value component enum and
    # the free-text device_brand cannot hold that; they stay for the component
    # hint and migration history, while the governed links below carry the
    # real taxonomy (shared with fix.catalogue.item — one master, R1).
    category_id = fields.Many2one(
        "product.category",
        string="Product Category (Group Tree)",
        index=True,
        help="Level 1 = the file's Group, level 2 = its Category — the seeded "
        "product.category tree (report R3).",
    )
    brand_id = fields.Many2one(
        "fix.brand", string="Brand (Brand Master)", index=True, help="Governed fix.brand record"
    )
    model_compatibility_ids = fields.Many2many(
        "fix.device.model",
        "fix_spare_part_device_model_rel",
        "part_id",
        "model_id",
        string="Compatible Device Models",
        help="Governed device-model compatibility (replaces the free-text matrix; "
        "report R8.2 keeps this empty until the model column is cleansed).",
    )

    # The three part identities, surfaced on the spare part through the
    # purchased-as product (product.product delegates to product.template).
    # Writable relations so the 7-tab master form (M15-form-part) captures
    # them in one place — no second master to maintain (report R1).
    product_default_code = fields.Char(
        related="product_id.default_code",
        string="New ERP Part No (SKU)",
        store=False,
        readonly=False,
    )
    product_manufacturer_part_number = fields.Char(
        related="product_id.manufacturer_part_number",
        string="Manufacturer Part No (MPN)",
        store=False,
        readonly=False,
    )
    product_legacy_erp_part_number = fields.Char(
        related="product_id.legacy_erp_part_number",
        string="Previous ERP Part No",
        store=False,
        readonly=False,
    )
    uom = fields.Char(string="Unit of Measure", default="PCS")
    state = fields.Selection(
        [("active", "Active"), ("discontinued", "Discontinued"), ("obsolete", "Obsolete")],
        string="Status",
        default="active",
        tracking=True,
    )

    compatibility_notes = fields.Text(string="Device Compatibility Matrix")
    compatible_models = fields.Text(string="Compatible Models / Hardware Matrix")
    is_serialized = fields.Boolean(
        string="Serialized Component",
        default=False,
        help="Mandates individual serial number tracking on receipt and consumption",
    )
    core_exchange_required = fields.Boolean(
        string="Core Return Required",
        default=False,
        help="Customer or workshop must return the defective part for reverse logistics / e-waste",
    )

    warranty_months = fields.Integer(string="Warranty Period (Months)", default=6)
    unit_cost = fields.Float(string="Standard Cost (BDT)", default=0.0, groups=COST_GROUP)
    list_price = fields.Float(string="List Price (BDT)", default=0.0)

    product_id = fields.Many2one(
        "product.product",
        string="Purchased As (Product)",
        index=True,
        ondelete="restrict",
        help="The product M16 purchase orders buy this part as. A PO goods receipt of "
        "this product posts the received quantity into the M15 ledger (A06 M15-9).",
    )
    onhand_ids = fields.One2many("fix.stock.onhand", "part_id", string="Location Ledger")
    qty_available = fields.Float(
        string="Quantity On Hand",
        compute="_compute_ledger_totals",
        store=True,
        readonly=True,
        help="Sum of the location ledger, every class and status. Never typed.",
    )
    qty_reserved = fields.Float(
        string="Quantity Reserved",
        compute="_compute_ledger_totals",
        store=True,
        readonly=True,
    )
    average_cost = fields.Float(
        string="Average Cost (BDT)",
        compute="_compute_ledger_totals",
        store=True,
        readonly=True,
        groups=COST_GROUP,
        help="Weighted average of the owned ledger buckets (consignment and customer "
        "property excluded); the standard cost when nothing is on hand.",
    )
    storage_class = fields.Selection(
        [("general", "General"), ("hazardous", "Hazardous (Li-ion / chemical)")],
        string="Storage Class",
        compute="_compute_storage_class",
        store=True,
        readonly=False,
        help="BRU-WMS-11: hazardous parts are put away only into hazardous bins.",
    )
    min_qty = fields.Float(string="Minimum Reorder Point", default=5.0)
    max_qty = fields.Float(string="Target Max Stock", default=25.0)
    safety_stock = fields.Float(string="Safety Buffer Stock", default=3.0)
    criticality = fields.Selection(
        [
            ("low", "Low — substitute available"),
            ("medium", "Medium — affects cycle time"),
            ("high", "High — blocks repair"),
            ("critical", "Critical — no substitute, SLA risk"),
        ],
        default="medium",
        help="Used by the ABC/XYZ/criticality view: critical parts always stock at safety level",
    )

    active = fields.Boolean(default=True)
    legacy_reference = fields.Char(
        string="Legacy Reference",
        index=True,
        readonly=True,
        copy=False,
        help="MIG-03: permanent source-system reference written by the inventory "
        "loader (migrations/load_inventory.py) - never edited, never copied",
    )

    _part_number_company_unique = models.Constraint(
        "UNIQUE (part_number, company_id)",
        "Part number must be unique per company.",
    )
    _part_code_unique = _part_number_company_unique
    _product_company_unique = models.Constraint(
        "UNIQUE (product_id, company_id)",
        "A purchased product maps to one spare part per company.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"qty_available", "qty_reserved", "state"}

    @api.depends("onhand_ids.qty", "onhand_ids.reserved", "onhand_ids.unit_cost", "unit_cost")
    def _compute_ledger_totals(self):
        for part in self:
            rows = part.onhand_ids
            part.qty_available = round(sum(rows.mapped("qty")), 4)
            part.qty_reserved = round(sum(rows.mapped("reserved")), 4)
            valued = rows.filtered(lambda r: r.ownership_class in VALUED_CLASSES and r.qty > 0)
            qty = sum(valued.mapped("qty"))
            part.average_cost = (
                round(sum(r.qty * (r.unit_cost or 0.0) for r in valued) / qty, 4)
                if qty
                else part.unit_cost or 0.0
            )

    @api.depends("part_category")
    def _compute_storage_class(self):
        for part in self:
            if not part.storage_class:
                part.storage_class = "hazardous" if part.part_category == "battery" else "general"

    def write(self, vals):
        if self and "unit_cost" in vals and not self._fix_guard_open():
            changed = self.filtered(
                lambda p: abs((p.unit_cost or 0.0) - float(vals["unit_cost"] or 0.0)) > 1e-6
            )
            if changed:
                raise UserError(
                    "The standard cost of %s changes only through Set Standard Cost by an "
                    "Inventory Controller (issues are valued at the ledger average cost)."
                    % ", ".join(changed.mapped("part_number"))
                )
        if self and "is_serialized" in vals and not self._fix_guard_open():
            # the form now offers it: stock already held has no serials to issue
            holding = self.filtered(
                lambda p: bool(p.is_serialized) != bool(vals["is_serialized"]) and p.qty_available
            )
            if holding:
                raise UserError(
                    "%s holds stock: serial control is changed only when nothing is on hand."
                    % ", ".join(holding.mapped("part_number"))
                )
        return super().write(vals)

    # ---- controlled master-data changes ------------------------------------
    def _part_check_controller(self):
        if not self.env.su and not self.env.user.has_group(CONTROLLER_GROUP):
            raise UserError("Only an Inventory Controller can change a part's status or cost.")

    def action_set_standard_cost(self, cost):
        """Change the standard (reference) cost. Ledger buckets keep their
        own average cost; revaluing stock is fix.stock.onhand._fix_revalue."""
        self._part_check_controller()
        cost = float(cost or 0.0)
        if cost < 0:
            raise UserError("A standard cost cannot be negative.")
        for part in self:
            before = part.unit_cost
            part._guarded().write({"unit_cost": cost})
            part.message_post(
                body="Standard cost changed %.2f -> %.2f by %s."
                % (before, cost, self.env.user.name)
            )
        return True

    def _part_set_state(self, state):
        self._part_check_controller()
        self._guarded().write({"state": state})
        return True

    def action_discontinue(self):
        return self._part_set_state("discontinued")

    def action_mark_obsolete(self):
        return self._part_set_state("obsolete")

    def action_reactivate(self):
        return self._part_set_state("active")

    @api.constrains("min_qty", "max_qty")
    def _check_min_max_quantities(self):
        for part in self:
            if part.min_qty < 0 or part.max_qty < 0:
                raise ValidationError("Inventory threshold quantities cannot be negative.")
            if part.max_qty < part.min_qty:
                raise ValidationError(
                    "Target maximum stock cannot be less than minimum reorder threshold."
                )

    def find_by_code(self, scanned_code: str) -> FixSparePart:
        """Find part record by barcode, QR code, or part number. A blank scan
        finds nothing (`= ''` also matches NULL columns in the ORM, so a
        blank code used to resolve to an arbitrary un-barcoded part)."""
        clean = (scanned_code or "").strip()
        if not clean:
            return self.browse()
        part = self.search(
            [
                "|",
                "|",
                ("barcode", "=", clean),
                ("qr_code", "=", clean),
                ("part_number", "=", clean),
            ],
            limit=1,
        )
        return part
