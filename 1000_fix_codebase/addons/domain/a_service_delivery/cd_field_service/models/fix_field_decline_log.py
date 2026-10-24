# fix.field.decline.log — Audit Trail for Declined Dispatches (CD-M02-01)
from odoo import api, fields, models


class FixFieldDeclineLog(models.Model):
    """Audit log recording technician dispatch declines with reason taxonomy for SLA analysis."""

    _name = "fix.field.decline.log"
    _description = "Field Dispatch Decline Log"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "decline_date desc, id desc"

    # Multi-tenant scoping per AS-03
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Operating Unit",
        required=True,
        index=True,
    )

    name = fields.Char(
        string="Log Reference",
        required=True,
        copy=False,
        readonly=True,
        default="/",
    )
    name_bn = fields.Char(
        string="Log Reference (Bengali)",
        help="DE-17 Bengali-first presentation",
    )

    field_order_id = fields.Many2one(
        "fix.field.order",
        string="Field Order",
        required=True,
        ondelete="cascade",
        index=True,
    )
    technician_id = fields.Many2one(
        "hr.employee",
        string="Declining Technician",
        required=True,
        index=True,
    )
    decline_date = fields.Datetime(
        string="Decline Timestamp",
        default=fields.Datetime.now,
        required=True,
    )
    reason = fields.Selection(
        [
            ("capacity", "Capacity Exceeded / Overbooked"),
            ("distance", "Outside Commute Range"),
            ("skill_gap", "Missing Tool / Skill Requirement"),
            ("emergency", "Personal / Vehicle Emergency"),
            ("other", "Other Reason"),
        ],
        string="Decline Reason",
        required=True,
        index=True,
    )
    notes = fields.Text(string="Technician Notes")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                seq = self.env["ir.sequence"].next_by_code("fix.field.decline.log")
                vals["name"] = (
                    seq or f"DEC/{fields.Date.today().year}/{self.search_count([]) + 1:04d}"
                )
            if not vals.get("name_bn") and vals.get("name"):
                vals["name_bn"] = vals["name"]
        return super().create(vals_list)
