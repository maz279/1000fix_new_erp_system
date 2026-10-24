# fix.workshop.part.line — Consumed Spare Part Line (CD-M31-01 / M15 Integration).
import logging

from odoo import api, fields, models

logger = logging.getLogger(__name__)


class FixWorkshopPartLine(models.Model):
    """A spare part consumed during execution of a workshop repair job.

    Integrates with M15 cd_inventory for barcode scanning, stock decrements,
    and suspense valuation postings.
    """

    _name = "fix.workshop.part.line"
    _description = "Workshop Consumed Part Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "job_id, id"

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
    job_id = fields.Many2one(
        "fix.workshop.job",
        string="Workshop Job",
        required=True,
        ondelete="cascade",
        index=True,
    )

    product_id = fields.Many2one(
        "product.product",
        string="Spare Part",
        required=True,
        index=True,
    )
    part_number = fields.Char(
        string="SKU / Part Number",
        related="product_id.default_code",
        store=True,
    )
    # Not stored: a stored related of the translatable product name is computed in
    # one language only (Odoo warns); nothing needs a frozen snapshot of the name.
    part_name = fields.Char(
        string="Part Description",
        related="product_id.name",
    )
    quantity = fields.Float(
        string="Quantity",
        default=1.0,
        required=True,
    )

    # AS-10: Monetary total with currency
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.ref("base.BDT", raise_if_not_found=False)
        or self.env.company.currency_id,
    )
    unit_cost = fields.Monetary(
        string="Unit Cost",
        currency_field="currency_id",
    )
    subtotal = fields.Monetary(
        string="Subtotal",
        compute="_compute_subtotal",
        store=True,
        currency_field="currency_id",
    )

    lot_serial_number = fields.Char(
        string="Serial / Lot Number",
        help="Serial number of the replaced component for parts genealogy tracking",
    )
    consumption_ref = fields.Char(
        string="Stock Consumption Ref",
        help="Linked M15 consumption transaction reference",
    )
    notes = fields.Char(string="Fitment Notes")

    @api.depends("quantity", "unit_cost")
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = (rec.quantity or 0.0) * (rec.unit_cost or 0.0)

    @api.onchange("product_id")
    def _onchange_product_id(self):
        if self.product_id:
            self.unit_cost = self.product_id.standard_price
