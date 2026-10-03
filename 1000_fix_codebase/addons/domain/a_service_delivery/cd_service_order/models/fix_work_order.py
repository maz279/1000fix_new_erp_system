# fix.work.order — the repair execution unit (P04-M03-T02).
from odoo import api, fields, models


class FixWorkOrder(models.Model):
    """A work order — the technician's unit of work within a service order."""
    _name = "fix.work.order"
    _description = "Work Order"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "order_id, sequence"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit")

    order_id = fields.Many2one("fix.service.order", string="Service Order",
                               required=True, ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    name = fields.Char(compute="_compute_name", store=True)

    technician_id = fields.Many2one("hr.employee", string="Technician")
    state = fields.Selection(
        [("pending", "Pending"), ("assigned", "Assigned"),
         ("in_progress", "In Progress"), ("completed", "Completed"),
         ("failed", "Failed")],
        default="pending", required=True, tracking=True)

    # Diagnostic (T05: guided diagnostic tree)
    diagnostic_tree_id = fields.Many2one("fix.diagnostic.node", string="Diagnostic Path")
    diagnosed_fault_code = fields.Char(string="Fault Code",
                                       help="From the diagnostic tree's terminal node")

    # Time tracking
    start_time = fields.Datetime()
    end_time = fields.Datetime()
    duration_hours = fields.Float(compute="_compute_duration", store=True)

    # Parts consumed (from the catalogue)
    parts_consumed_ids = fields.One2many("fix.work.order.part", "work_order_id",
                                         string="Parts Consumed")
    notes = fields.Text()

    @api.depends("order_id", "sequence")
    def _compute_name(self):
        for rec in self:
            rec.name = f"{rec.order_id.name}/W{rec.sequence:02d}"

    @api.depends("start_time", "end_time")
    def _compute_duration(self):
        for rec in self:
            if rec.start_time and rec.end_time:
                delta = rec.end_time - rec.start_time
                rec.duration_hours = delta.total_seconds() / 3600
            else:
                rec.duration_hours = 0.0


class FixWorkOrderPart(models.Model):
    """A part consumed during a work order."""
    _name = "fix.work.order.part"
    _description = "Work Order Part"

    work_order_id = fields.Many2one("fix.work.order", required=True, ondelete="cascade")
    product_id = fields.Many2one("product.product", string="Part", required=True)
    quantity = fields.Float(default=1.0, digits="Product Unit of Measure")
    # AS-10: Monetary
    unit_cost = fields.Monetary(string="Unit Cost", currency_field="currency_id")
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
