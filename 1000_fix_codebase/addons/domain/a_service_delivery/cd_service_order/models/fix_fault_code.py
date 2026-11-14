# fix.fault.code — the fault & symptom taxonomy master (M01, FR-SRM-077 support).
# Faults lived as free text (fix.service.order.fault.fault_code, work orders,
# diagnostic trees); this master makes the taxonomy selectable, consistent
# and reportable — the backbone of the Fault & Symptom Coding screen and the
# Rework & Repeat-Fault analysis.
from odoo import api, fields, models

FAULT_CATEGORIES = [
    ("power", "Power / No-boot"),
    ("display", "Display / Graphics"),
    ("battery_charging", "Battery & Charging"),
    ("input", "Keyboard / Touch / Input"),
    ("audio", "Audio / Mic / Speaker"),
    ("camera", "Camera / Sensors"),
    ("network", "Network / Connectivity"),
    ("software", "OS / Software"),
    ("physical", "Physical / Liquid Damage"),
    ("thermal", "Thermal / Fan"),
    ("storage", "Storage / Data"),
    ("none", "No Fault Found"),
]


class FixFaultCode(models.Model):
    """A fault/symptom code in the estate-wide repair taxonomy."""

    _name = "fix.fault.code"
    _description = "Fault & Symptom Code"
    _order = "category, code"

    code = fields.Char(
        required=True,
        index=True,
        help="Short stable code, e.g. PWR-01. Referenced by fault lines, "
        "work orders and diagnostic terminals.",
    )
    name = fields.Char(required=True)
    category = fields.Selection(FAULT_CATEGORIES, required=True, default="power")
    default_severity = fields.Selection(
        [
            ("cosmetic", "Cosmetic"),
            ("functional", "Functional"),
            ("critical", "Critical"),
        ],
        default="functional",
        help="Default severity suggested when this code is picked on a "
        "fault line (FR-SRM-077 multi-fault severity).",
    )
    description = fields.Text()
    active = fields.Boolean(default=True)
    # M37 capture audit (2026-11-14), FR-CAT-042: a brand files a warranty
    # claim under ITS own fault code, so the taxonomy maps each code to the
    # brand's. The Fault Code form captures these as its lines.
    brand_code_ids = fields.One2many("fix.fault.brand.map", "fault_id", string="Brand Claim Codes")

    # Odoo 19 constraint (same pattern as fix.sla.policy)
    _code_unique = models.Constraint("UNIQUE (code)", "Fault code must be unique")

    @api.onchange("code")
    def _onchange_code(self):
        if self.code:
            self.code = self.code.strip().upper()


class FixFaultBrandMap(models.Model):
    """FR-CAT-042: the brand's own claim code for one of our fault codes."""

    _name = "fix.fault.brand.map"
    _description = "Fault Code - Brand Claim Code"
    _order = "fault_id, brand_id"
    _rec_name = "brand_code"

    fault_id = fields.Many2one(
        "fix.fault.code", string="Fault Code", required=True, index=True, ondelete="cascade"
    )
    brand_id = fields.Many2one("fix.brand", string="Brand", required=True, ondelete="restrict")
    brand_code = fields.Char(string="Brand Claim Code", required=True)
    brand_description = fields.Char(string="Brand Wording")

    _one_code_per_brand = models.Constraint(
        "UNIQUE (fault_id, brand_id)", "A fault code maps to one claim code per brand."
    )
