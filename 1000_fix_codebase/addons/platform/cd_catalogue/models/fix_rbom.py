# M37 repair-BOM: the parts/services consumed by a catalogue service item,
# with the standard quantity. This is the repair BOM the registry's rBOM
# completeness report and the rBOM Line form read.
from odoo import api, fields, models
from odoo.exceptions import ValidationError

from .catalogue_roles import ROLE_OFFICER, require_role


class FixRbomLine(models.Model):
    _name = "fix.rbom.line"
    _description = "Repair BOM Line"
    _order = "item_id, sequence, id"

    # A04 audit (2026-11-04) M37-3: deleting the service item used to cascade
    # its rBOM lines away; a referenced item is now kept (BRU-CAT-03).
    item_id = fields.Many2one(
        "fix.catalogue.item", string="Service Item", required=True, ondelete="restrict", index=True
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
    # A04 audit M37-5 (rbom_02): a negative or zero standard quantity is not a
    # bill of materials; it lowers every cost and stock forecast built on it.
    _quantity_positive = models.Constraint(
        "CHECK (quantity > 0)",
        "An rBOM line needs a positive quantity.",
    )

    @staticmethod
    def _check_quantity_vals(vals):
        # Before the INSERT/UPDATE, so the user gets a ValidationError and not
        # the SQL CHECK's IntegrityError.
        if "quantity" in vals and (vals["quantity"] or 0.0) <= 0.0:
            raise ValidationError("An rBOM line needs a positive quantity.")

    @api.constrains("item_id", "component_item_id")
    def _check_no_cycle(self):
        """A04 audit M37-5 (rbom_01): A -> B -> A made every explosion of
        either item loop. A component may not (transitively) contain the item
        it is a component of (BRU-CAT-07 consistency)."""
        Line = self.sudo()
        for line in self:
            target = line.item_id.id
            seen = set()
            frontier = {line.component_item_id.id}
            while frontier:
                if target in frontier:
                    raise ValidationError(
                        "rBOM cycle: %s already contains %s, directly or through its own "
                        "components." % (line.component_item_id.name, line.item_id.name)
                    )
                seen |= frontier
                rows = Line.search([("item_id", "in", list(frontier))])
                frontier = set(rows.mapped("component_item_id").ids) - seen

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, (ROLE_OFFICER,), "Changing a repair BOM")
        for vals in vals_list:
            self._check_quantity_vals(vals)
        return super().create(vals_list)

    def write(self, vals):
        require_role(self.env, (ROLE_OFFICER,), "Changing a repair BOM")
        self._check_quantity_vals(vals)
        return super().write(vals)

    def unlink(self):
        require_role(self.env, (ROLE_OFFICER,), "Changing a repair BOM")
        return super().unlink()
