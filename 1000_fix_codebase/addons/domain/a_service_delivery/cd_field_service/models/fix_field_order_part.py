# fix.field.order.part — a part fitted (or returned) on a field job (CD-M02-01).
#
# A02 workflow audit (2026-11-03) M02 step 7, P2: the technician app's
# consume_part wrote a fix.work.order.part against an M01 work order the field
# order never saw, so a field job completed with no record of what went into
# the device, and completion checked nothing. A part is now a line on the field
# order itself: picked (planned) before or during the visit, then fitted
# (consumed) or returned by the assigned technician while on site. A fitted
# line is frozen and cannot be deleted, and completion refuses a job with a
# part still unresolved (picked, but neither fitted nor returned).
from odoo import api, fields, models
from odoo.exceptions import UserError

PART_STATES = [
    ("planned", "Picked / Planned"),
    ("consumed", "Fitted on Site"),
    ("returned", "Returned to Van Stock"),
]
GUARDED_PART_FIELDS = frozenset(
    {"state", "consumed_at", "consumed_by_id", "returned_reason", "source_ref"}
)
# what a fitted line, or any line of a closed field order, records
PART_FROZEN_FIELDS = frozenset(
    {"field_order_id", "product_id", "quantity", "unit_cost", "currency_id", "lot_serial_number"}
)
ORDER_CLOSED_STATES = ("completed", "cancelled")
ON_SITE_STATES = ("arrived", "in_progress")


class FixFieldOrderPart(models.Model):
    _name = "fix.field.order.part"
    _description = "Field Order Part Line"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "field_order_id, id"

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | GUARDED_PART_FIELDS

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self._m02_frozen():
            locked |= PART_FROZEN_FIELDS
        return locked

    field_order_id = fields.Many2one(
        "fix.field.order", string="Field Order", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(
        related="field_order_id.company_id", store=True, index=True, string="Company"
    )
    operating_unit_id = fields.Many2one(
        related="field_order_id.operating_unit_id", store=True, string="Operating Unit"
    )
    product_id = fields.Many2one("product.product", string="Spare Part", required=True)
    part_number = fields.Char(related="product_id.default_code", string="SKU / Part Number")
    quantity = fields.Float(default=1.0, required=True)
    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        default=lambda self: self.env.ref("base.BDT", raise_if_not_found=False)
        or self.env.company.currency_id,
    )
    unit_cost = fields.Monetary(string="Unit Cost", currency_field="currency_id")
    subtotal = fields.Monetary(
        compute="_compute_subtotal", store=True, currency_field="currency_id"
    )
    lot_serial_number = fields.Char(string="Serial / Lot Number")
    van_location_id = fields.Many2one(
        "fix.stock.location", string="Van Stock Location", ondelete="set null"
    )
    state = fields.Selection(
        PART_STATES, default="planned", required=True, readonly=True, tracking=True, index=True
    )
    consumed_at = fields.Datetime(string="Fitted At", readonly=True, copy=False)
    consumed_by_id = fields.Many2one("res.users", string="Fitted By", readonly=True, copy=False)
    returned_reason = fields.Char(string="Return Reason", readonly=True, copy=False)
    source_ref = fields.Char(
        string="Source",
        readonly=True,
        copy=False,
        help="Where the line was recorded: the workspace, or the offline command id.",
    )

    @api.depends("quantity", "unit_cost")
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = (rec.quantity or 0.0) * (rec.unit_cost or 0.0)

    def _m02_frozen(self) -> bool:
        self.ensure_one()
        return self.state == "consumed" or (self.field_order_id.sudo().state in ORDER_CLOSED_STATES)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            order = self.env["fix.field.order"].sudo().browse(vals.get("field_order_id"))
            if order.exists() and order.state in ORDER_CLOSED_STATES and not self.env.su:
                raise UserError(
                    "Parts cannot be added to field order %s: it is %s." % (order.name, order.state)
                )
            if "quantity" in vals and (vals["quantity"] or 0.0) <= 0:
                raise UserError("A part line needs a quantity above zero.")
            if order.exists() and not vals.get("van_location_id") and order.van_location_id:
                vals["van_location_id"] = order.van_location_id.id
            if "unit_cost" not in vals and vals.get("product_id"):
                product = self.env["product.product"].sudo().browse(vals["product_id"])
                vals["unit_cost"] = product.standard_price
        return super().create(vals_list)

    def write(self, vals):
        touched = PART_FROZEN_FIELDS & set(vals)
        if self and touched and not self._fix_guard_open():
            for rec in self:
                if not rec._m02_frozen():
                    continue
                changed = sorted(n for n in touched if rec._fix_guard_differs(n, vals[n], rec[n]))
                if changed:
                    raise UserError(
                        "%s cannot be changed on a %s part line: it is the record of what "
                        "went into the customer's device."
                        % (
                            ", ".join(rec._fields[n].string or n for n in changed),
                            "fitted" if rec.state == "consumed" else "closed field order's",
                        )
                    )
        return super().write(vals)

    def unlink(self):
        if not self._fix_guard_open():
            for rec in self:
                if rec._m02_frozen():
                    raise UserError(
                        "Part line %s on %s cannot be deleted: fitted parts stay on the job."
                        % (rec.part_number or rec.product_id.display_name, rec.field_order_id.name)
                    )
        return super().unlink()

    def _m02_check_on_site(self, what):
        for rec in self:
            order = rec.field_order_id
            if rec.state != "planned":
                raise UserError("Part line %s is already %s." % (rec.display_name, rec.state))
            if order.state not in ON_SITE_STATES:
                raise UserError(
                    "Parts are %s on site, while field order %s is arrived or in progress "
                    "(it is %s)." % (what, order.name, order.state)
                )
            # only the technician the order is assigned to (superuser: the
            # offline sync, which checks the assignment itself)
            order._fix_require_assigned_technician("record parts on")

    def action_consume(self):
        """The assigned technician fits the part on site."""
        self._m02_check_on_site("fitted")
        for rec in self:
            rec._guarded().write(
                {
                    "state": "consumed",
                    "consumed_at": fields.Datetime.now(),
                    "consumed_by_id": self.env.user.id,
                    "source_ref": rec.source_ref or "workspace",
                }
            )
        return True

    def action_return(self, reason=""):
        """A picked part that was not fitted goes back to the van stock."""
        reason = (reason or "").strip()
        if not reason:
            raise UserError("Say why the part was not fitted.")
        self._m02_check_on_site("returned")
        for rec in self:
            rec._guarded().write({"state": "returned", "returned_reason": reason})
        return True


class FixFieldOrderParts(models.Model):
    _inherit = "fix.field.order"

    part_line_ids = fields.One2many("fix.field.order.part", "field_order_id", string="Parts")
    parts_total = fields.Monetary(
        string="Parts Fitted (BDT)",
        compute="_compute_parts_total",
        currency_field="currency_id",
    )

    @api.depends("part_line_ids.subtotal", "part_line_ids.state")
    def _compute_parts_total(self):
        for rec in self:
            rec.parts_total = sum(
                rec.part_line_ids.filtered(lambda ln: ln.state == "consumed").mapped("subtotal")
            )

    def _fix_parts_unresolved(self):
        """Picked parts neither fitted nor returned: completion waits for them
        (A02 audit M02 step 7)."""
        self.ensure_one()
        return self.sudo().part_line_ids.filtered(lambda ln: ln.state == "planned")
