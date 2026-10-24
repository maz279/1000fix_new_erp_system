# fix_facility — M47: facility, branch infrastructure & maintenance work orders (P10-M05 / R08-M03).
from datetime import datetime

from odoo import api, fields, models

from libs.py.fix_events import publish


class FixSite(models.Model):
    _name = "fix.site"
    _description = "Site / Facility"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    site_type = fields.Selection(
        [
            ("branch", "Service Branch"),
            ("warehouse", "Warehouse"),
            ("office", "Corporate Office"),
            ("data_centre", "Data Centre"),
        ],
        required=True,
        default="branch",
    )
    branch_id = fields.Many2one("fix.branch", string="Branch (M30)", ondelete="set null")
    address = fields.Text()
    floor_area_sqm = fields.Float(string="Floor Area (sqm)")
    lease_start = fields.Date()
    lease_end = fields.Date()
    monthly_rent = fields.Float(string="Monthly Rent (BDT)")
    equipment_ids = fields.Many2many(
        "fix.equipment",
        string="Linked Site Assets",
        help="Equipments deployed at this facility (M46)",
    )
    work_order_ids = fields.One2many("fix.facility.work.order", "site_id", string="Work Orders")
    state = fields.Selection(
        [("active", "Active"), ("closed", "Closed")], default="active", required=True, tracking=True
    )

    def action_link_assets(self):
        for rec in self:
            publish(
                self.env,
                "site.assets_linked",
                "fix.site",
                rec.id,
                {"site": rec.name, "assets_count": len(rec.equipment_ids)},
            )

    def action_close(self):
        for rec in self:
            rec.state = "closed"

    def action_reopen(self):
        for rec in self:
            rec.state = "active"


class FixFacilityWorkOrder(models.Model):
    _name = "fix.facility.work.order"
    _description = "Facility Work Order"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, default="New")
    site_id = fields.Many2one("fix.site", string="Site", required=True, ondelete="cascade")
    equipment_id = fields.Many2one(
        "fix.equipment",
        string="Target Equipment",
        help="Target infrastructure asset from cd_equipment_register (M46)",
    )
    work_type = fields.Selection(
        [
            ("maintenance", "Preventive Maintenance"),
            ("repair", "Emergency Repair"),
            ("upgrade", "Infrastructure Upgrade"),
            ("inspection", "Compliance Inspection"),
        ],
        required=True,
        default="maintenance",
    )
    description = fields.Text(required=True)
    assigned_to = fields.Many2one("hr.employee", string="Assigned Engineer")
    scheduled_date = fields.Date(default=fields.Date.context_today)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    estimated_cost = fields.Monetary(string="Estimated Cost", currency_field="currency_id")
    actual_cost = fields.Monetary(string="Actual Cost", currency_field="currency_id")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("scheduled", "Scheduled"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.facility.work.order")
                    or f"FWO/{datetime.now().strftime('%Y%m%d%H%M%S')}"
                )
        return super().create(vals_list)

    def action_schedule(self, date=None):
        for rec in self:
            if date:
                rec.scheduled_date = date
            rec.state = "scheduled"

    def action_start(self):
        for rec in self:
            rec.state = "in_progress"

    def action_complete(self):
        for rec in self:
            rec.state = "completed"
            publish(
                self.env,
                "facility.work_order_completed",
                "fix.facility.work.order",
                rec.id,
                {
                    "order": rec.name,
                    "site": rec.site_id.name,
                    "work_type": rec.work_type,
                    "cost": float(rec.actual_cost or rec.estimated_cost or 0.0),
                },
            )

    def action_cancel(self):
        for rec in self:
            rec.state = "cancelled"
