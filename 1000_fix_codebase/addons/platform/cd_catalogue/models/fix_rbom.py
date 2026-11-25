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
    # A04 ERP audit (20 Nov 2026) M37-F12: the rBOM is its service item's
    # company's (the company rule reads this).
    company_id = fields.Many2one(related="item_id.company_id", store=True, index=True)
    sequence = fields.Integer(default=10)
    quantity = fields.Float(required=True, default=1.0)
    note = fields.Char()
    # M37 capture audit, third pass (2026-11-19), FR-CAT-022: the rBOM is per
    # operation PER MODEL, with a criticality and permitted alternates.
    device_model_id = fields.Many2one(
        "fix.device.model",
        string="Device Model",
        index=True,
        ondelete="restrict",
        help="Blank: the line applies to every model the operation covers.",
    )
    criticality = fields.Selection(
        [
            ("critical", "Critical: the repair cannot proceed without it"),
            ("standard", "Standard: normally replaced"),
            ("conditional", "Conditional: replaced if found faulty"),
        ],
        string="Criticality",
        required=True,
        default="standard",
    )
    alternate_group = fields.Char(
        string="Alternate Group",
        help="Lines sharing a group are alternates: any ONE of them satisfies the operation.",
    )

    # One line per component per model. The model is nullable, and a SQL
    # UNIQUE lets NULL twins in, so _check_no_twin covers the blank model.
    _unique_component = models.Constraint(
        "UNIQUE (item_id, component_item_id, device_model_id)",
        "One rBOM line per component per model on a service item.",
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

    @api.constrains("item_id", "component_item_id", "device_model_id")
    def _check_no_twin(self):
        for line in self.filtered(lambda r: not r.device_model_id):
            if self.search_count(
                [
                    ("id", "!=", line.id),
                    ("item_id", "=", line.item_id.id),
                    ("component_item_id", "=", line.component_item_id.id),
                    ("device_model_id", "=", False),
                ]
            ):
                raise ValidationError(
                    "%s is already on %s's rBOM for every model."
                    % (line.component_item_id.name, line.item_id.name)
                )

    @api.constrains("item_id", "component_item_id", "device_model_id")
    def _check_model_compatibility(self):
        """BRU-CAT-07: an rBOM line may reference only parts compatible with
        the operation's declared models."""
        for line in self:
            operation_models = line.item_id.device_model_ids
            if (
                line.device_model_id
                and operation_models
                and line.device_model_id not in operation_models
            ):
                raise ValidationError(
                    "%s is not one of the models %s is declared for (BRU-CAT-07)."
                    % (line.device_model_id.display_name, line.item_id.name)
                )
            scope = line.device_model_id or operation_models
            clash = self.env["fix.model.compatibility"]._incompatible(line.component_item_id, scope)
            if clash:
                raise ValidationError(
                    "%s does not fit %s (model compatibility, BRU-CAT-07): %s"
                    % (
                        line.component_item_id.name,
                        ", ".join(clash.mapped("device_model_id.display_name")),
                        clash[:1].note,
                    )
                )

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


# Deeper than this an explosion is a data error, not a bill of materials.
_MAX_DEPTH = 8


class FixCatalogueItemExplosion(models.Model):
    """A04 ERP audit (20 Nov 2026) M37-F3 (FR-CAT-028 / FR-CAT-041): a
    service's repair BOM and a bundle's kit never exploded into the lines an
    estimate quotes or into the parts M15 / M41 must supply. This is the
    explosion every consumer reads."""

    _inherit = "fix.catalogue.item"

    def _fix_explode(self, qty=1.0, device_model=None, include_optional=False, _depth=0):
        """The leaf lines `qty` of this item consume, as a list of dicts:
        {item, product, qty, criticality, alternate_group, source}.

        - rBOM lines of the device model (and the all-model lines). Of an
          alternate group only the first line is taken: any one satisfies the
          operation; the rest are its permitted substitutes.
        - kit components of the item's active kits that explode at quotation
          (optional components only when asked).
        - a component that is itself a service / bundle explodes in turn;
          a part is a leaf. An item with neither is its own leaf."""
        self.ensure_one()
        if _depth > _MAX_DEPTH:
            raise ValidationError(
                "%s explodes deeper than %d levels; check its repair BOM and kits."
                % (self.display_name, _MAX_DEPTH)
            )
        item = self.sudo()
        out = []
        lines = item.env["fix.rbom.line"].search([("item_id", "=", item.id)])
        if device_model:
            lines = lines.filtered(
                lambda r: not r.device_model_id or r.device_model_id == device_model
            )
            # a model-specific line replaces the all-model line of the same part
            specific = lines.filtered("device_model_id").mapped("component_item_id")
            lines = lines.filtered(
                lambda r: r.device_model_id or r.component_item_id not in specific
            )
        seen_groups = set()
        for line in lines.sorted(lambda r: (r.sequence, r.id)):
            group = (line.alternate_group or "").strip()
            if group:
                if group in seen_groups:
                    continue
                seen_groups.add(group)
            out += line.component_item_id._fix_explode_leaf(
                qty * line.quantity,
                device_model,
                include_optional,
                _depth,
                criticality=line.criticality,
                alternate_group=group or False,
                source="rbom",
            )
        Kit = item.env["fix.service.kit"]
        kits = Kit.search(
            [("catalogue_item_id", "=", item.id), ("explode_at", "in", ("quotation", "both"))]
        )
        for comp in kits.mapped("component_ids"):
            if comp.is_optional and not include_optional:
                continue
            product = comp.product_id
            component_item = product.product_tmpl_id.catalogue_item_id[:1] if product else None
            if component_item:
                out += component_item._fix_explode_leaf(
                    qty * comp.quantity,
                    device_model,
                    include_optional,
                    _depth,
                    criticality="conditional" if comp.is_optional else "standard",
                    alternate_group=False,
                    source="kit",
                )
            else:
                out.append(
                    {
                        "item": item.browse(),
                        "product": product,
                        "qty": qty * comp.quantity,
                        "criticality": "standard",
                        "alternate_group": False,
                        "source": "kit",
                        "description": comp.notes or (product.display_name if product else ""),
                    }
                )
        return out

    def _fix_explode_leaf(self, qty, device_model, include_optional, depth, **meta):
        self.ensure_one()
        item = self.sudo()
        has_children = item.env["fix.rbom.line"].search_count([("item_id", "=", item.id)]) or (
            item.env["fix.service.kit"].search_count(
                [("catalogue_item_id", "=", item.id), ("explode_at", "in", ("quotation", "both"))]
            )
        )
        if has_children and item.item_type not in ("part", "accessory", "finished_good"):
            return item._fix_explode(qty, device_model, include_optional, depth + 1)
        # M37-F11 (FR-CAT-033/BRU-CAT-07): a part that does not fit the device
        # is never put on its estimate or its parts demand.
        if device_model:
            clash = item.env["fix.model.compatibility"]._incompatible(item, device_model)
            if clash:
                raise ValidationError(
                    "%s does not fit %s (model compatibility, BRU-CAT-07): %s"
                    % (item.name, device_model.display_name, clash[:1].note or "")
                )
        return [
            dict(
                meta,
                item=item,
                product=item.product_tmpl_id.product_variant_id,
                qty=qty,
                description=item.name or "",
            )
        ]

    def _fix_part_demand(self, qty=1.0, device_model=None):
        """The stock demand `qty` of this item creates, for M15 reservation and
        M41 planning: {product.product: quantity} over the physical leaves of
        the explosion (parts, accessories, finished goods)."""
        self.ensure_one()
        demand = {}
        for row in self._fix_explode(qty, device_model):
            product, leaf = row["product"], row["item"]
            if not product or (
                leaf and leaf.item_type not in ("part", "accessory", "finished_good")
            ):
                continue
            demand[product] = demand.get(product, 0.0) + row["qty"]
        return demand
