# fix_service_order_fault — FR-SRM-077 Multi-Fault Handling per Device (CD-M01-01).
from odoo import fields, models


class FixServiceOrderFault(models.Model):
    _name = "fix.service.order.fault"
    _description = "Service Order Fault Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence asc, id asc"

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

    order_id = fields.Many2one(
        "fix.service.order",
        string="Service Order",
        required=True,
        ondelete="cascade",
        index=True,
    )
    sequence = fields.Integer(default=10)
    fault_code = fields.Char(string="Fault Code", index=True)
    description = fields.Text(string="Fault Description", required=True)
    severity = fields.Selection(
        [
            ("cosmetic", "Cosmetic / Minor"),
            ("functional", "Functional Impairment"),
            ("critical", "Complete Failure / Power Inoperable"),
        ],
        string="Severity",
        default="functional",
        required=True,
    )
    estimate_bdt = fields.Monetary(
        string="Estimate (BDT)",
        currency_field="currency_id",
        default=0.0,
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.ref("base.BDT", raise_if_not_found=False)
        or self.env.company.currency_id,
    )
    is_approved = fields.Boolean(
        string="Customer Approved",
        default=False,
        help="FR-SRM-077: Independent estimate and approval tracking per fault.",
    )
    repaired = fields.Boolean(string="Repaired & Verified", default=False)
