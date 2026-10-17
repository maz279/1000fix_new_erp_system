# cd_inventory — Spare Parts Master & Device Compatibility (M15, CD-M15-01).
from __future__ import annotations

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FixSparePart(models.Model):
    """Spare parts master record with device compatibility and serialized tracking."""

    _name = "fix.spare.part"
    _description = "Spare Part & Component"
    _inherit = ["mail.thread", "mail.activity.mixin"]

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
    unit_cost = fields.Float(string="Standard Cost (BDT)", default=0.0)
    list_price = fields.Float(string="Retail Replacement Price (BDT)", default=0.0)

    qty_available = fields.Float(string="Quantity On Hand", default=0.0, tracking=True)
    qty_reserved = fields.Float(string="Quantity Reserved", default=0.0)
    min_qty = fields.Float(string="Minimum Reorder Point", default=5.0)
    max_qty = fields.Float(string="Target Max Stock", default=25.0)
    safety_stock = fields.Float(string="Safety Buffer Stock", default=3.0)

    active = fields.Boolean(default=True)

    _part_number_company_unique = models.Constraint(
        "UNIQUE (part_number, company_id)",
        "Part number must be unique per company.",
    )
    _part_code_unique = _part_number_company_unique

    @api.constrains("min_qty", "max_qty")
    def _check_min_max_quantities(self):
        for part in self:
            if part.min_qty < 0 or part.max_qty < 0:
                raise ValidationError("Inventory threshold quantities cannot be negative.")
            if part.max_qty < part.min_qty:
                raise ValidationError("Target maximum stock cannot be less than minimum reorder threshold.")

    def find_by_code(self, scanned_code: str) -> FixSparePart:
        """Find part record by barcode, QR code, or part number."""
        clean = (scanned_code or "").strip()
        part = self.search([
            "|", "|",
            ("barcode", "=", clean),
            ("qr_code", "=", clean),
            ("part_number", "=", clean),
        ], limit=1)
        return part
