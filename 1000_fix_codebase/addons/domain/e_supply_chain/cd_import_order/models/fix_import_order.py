# fix_import_order — M44: import, landed cost (P09-M07).
from odoo import api, fields, models

from libs.py.fix_events import publish


class FixImportOrder(models.Model):
    """M44: import, trade compliance, landed cost. The M41<->M44 break:
    M44 CONSUMES goods.received events; M41 never calls M44."""
    _name = "fix.import.order"
    _description = "Import Order"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    supplier_id = fields.Many2one("res.partner", string="Supplier")
    country_origin = fields.Many2one("res.country", string="Country of Origin")
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.USD"))
    fob_value = fields.Monetary(string="FOB Value", currency_field="currency_id")
    freight_cost = fields.Monetary(string="Freight", currency_field="currency_id")
    insurance_cost = fields.Monetary(string="Insurance", currency_field="currency_id")
    customs_duty = fields.Monetary(string="Customs Duty", currency_field="currency_id")
    landed_cost = fields.Monetary(compute="_compute_landed",
                                  string="Landed Cost",
                                  currency_field="currency_id", store=True)
    state = fields.Selection(
        [("draft", "Draft"), ("shipped", "Shipped"), ("customs", "In Customs"),
         ("received", "Received"), ("landed", "Landed Cost Applied")],
        default="draft", required=True, tracking=True)

    @api.depends("fob_value", "freight_cost", "insurance_cost", "customs_duty")
    def _compute_landed(self):
        for rec in self:
            rec.landed_cost = (rec.fob_value + rec.freight_cost
                               + rec.insurance_cost + rec.customs_duty)

    def action_receive(self):
        for rec in self:
            rec.state = "received"
            publish(self.env, "goods.received", "fix.import.order", rec.id,
                    {"order": rec.name, "value": float(rec.fob_value)})
