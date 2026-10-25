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

    # Odoo 19 constraint (same pattern as fix.sla.policy)
    _code_unique = models.Constraint("UNIQUE (code)", "Fault code must be unique")

    @api.onchange("code")
    def _onchange_code(self):
        if self.code:
            self.code = self.code.strip().upper()
