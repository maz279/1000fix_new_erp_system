# M37 repair-BOM: the parts/services consumed by a catalogue service item,
# with the standard quantity. This is the repair BOM the registry's rBOM
# completeness report and the rBOM Line form read.
from odoo import fields, models


class FixRbomLine(models.Model):
    _name = "fix.rbom.line"
    _description = "Repair BOM Line"
    _order = "item_id, sequence, id"

    item_id = fields.Many2one(
        "fix.catalogue.item", string="Service Item", required=True, ondelete="cascade", index=True
    )
    component_item_id = fields.Many2one(
        "fix.catalogue.item",
        string="Component Item",
        required=True,
        ondelete="restrict",
        index=True,
    )
    sequence = fields.Integer(default=10)
    quantity = fields.Float(required=True, default=1.0)
    note = fields.Char()

    _unique_component = models.Constraint(
        "UNIQUE (item_id, component_item_id)",
        "One rBOM line per component on a service item.",
    )
    _no_self_reference = models.Constraint(
        "CHECK (item_id <> component_item_id)",
        "An rBOM component cannot be the service item itself.",
    )
