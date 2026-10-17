# fix_device_part_compatibility — M17 W2 Spare Parts Compatibility Matrix (CD-M17-02).
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FixDevicePartCompatibility(models.Model):
    _name = "fix.device.part.compatibility"
    _description = "Device Spare Part Compatibility Matrix"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "model_id asc, part_number asc"

    # AS-03: Multi-company and Operating Unit discipline
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Operating Unit",
        index=True,
    )

    model_id = fields.Many2one(
        "fix.device.model",
        string="Device Model",
        required=True,
        ondelete="cascade",
        index=True,
    )
    brand_id = fields.Many2one(
        related="model_id.brand_id",
        string="Brand",
        store=True,
        index=True,
    )
    part_number = fields.Char(string="Part Number / SKU", required=True, index=True)
    part_name = fields.Char(string="Part Description", required=True)
    category = fields.Selection(
        [
            ("display", "Display / Screen Assembly"),
            ("battery", "Battery Pack"),
            ("motherboard", "Logic Board / PCB"),
            ("charging_port", "Charging Port / Flex Cable"),
            ("camera", "Camera Module"),
            ("speaker", "Speaker / Audio Module"),
            ("casing", "Housing / Chassis"),
            ("consumable", "Adhesive / Screw / Thermal"),
        ],
        string="Part Category",
        default="display",
        required=True,
    )
    compatibility_type = fields.Selection(
        [
            ("oem", "Original Equipment Manufacturer (OEM)"),
            ("certified_aftermarket", "1000FiX Certified Grade-A Aftermarket"),
            ("incompatible", "Tested Incompatible / High Risk"),
        ],
        string="Compatibility Grade",
        default="oem",
        required=True,
        tracking=True,
    )
    active = fields.Boolean(default=True)
    notes = fields.Text(string="Engineering Compatibility Notes")

    _unique_model_part = models.Constraint(
        "UNIQUE (model_id, part_number)",
        "Part compatibility entry already exists for this device model.",
    )
