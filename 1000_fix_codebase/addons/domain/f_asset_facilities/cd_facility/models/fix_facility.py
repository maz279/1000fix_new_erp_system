# fix_facility — M47: facility, branch infrastructure (P10-M05).
from odoo import fields, models

from libs.py.fix_events import publish


class FixSite(models.Model):
    _name = "fix.site"
    _description = "Site / Facility"
    # P03 workspace data-entry form (discovered by cd_p03_portal).
    _p03_capture = {
        "module": "M47",
        "form": "Site",
        "fields": ["name", "site_type", "branch_id", "address", "floor_area_sqm",
                   "lease_start", "lease_end", "monthly_rent"],
    }
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    site_type = fields.Selection(
        [("branch", "Service Branch"), ("warehouse", "Warehouse"),
         ("office", "Corporate Office"), ("data_centre", "Data Centre")],
        required=True, default="branch")
    branch_id = fields.Many2one("fix.branch", string="Branch (M30)",
                                 ondelete="set null")
    address = fields.Text()
    floor_area_sqm = fields.Float(string="Floor Area (sqm)")
    lease_start = fields.Date()
    lease_end = fields.Date()
    monthly_rent = fields.Float(string="Monthly Rent (BDT)")
    state = fields.Selection([("active", "Active"), ("closed", "Closed")],
                              default="active", required=True, tracking=True)

    def action_link_assets(self):
        for rec in self:
            publish(self.env, "site.assets_linked", "fix.site", rec.id,
                    {"site": rec.name})


class FixFacilityWorkOrder(models.Model):
    _name = "fix.facility.work.order"
    _description = "Facility Work Order"
    # P03 workspace data-entry form (discovered by cd_p03_portal).
    _p03_capture = {
        "module": "M47",
        "form": "Facility Work Order",
        "fields": ["name", "site_id", "work_type", "description", "assigned_to",
                   "scheduled_date", "estimated_cost"],
    }
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    site_id = fields.Many2one("fix.site", string="Site", required=True,
                               ondelete="cascade")
    work_type = fields.Selection(
        [("maintenance", "Maintenance"), ("repair", "Repair"),
         ("upgrade", "Upgrade"), ("inspection", "Inspection")],
        required=True, default="maintenance")
    description = fields.Text(required=True)
    assigned_to = fields.Many2one("hr.employee", string="Assigned To")
    scheduled_date = fields.Date()
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    estimated_cost = fields.Monetary(string="Estimated Cost",
                                      currency_field="currency_id")
    state = fields.Selection([("draft", "Draft"), ("scheduled", "Scheduled"),
                              ("in_progress", "In Progress"),
                              ("completed", "Completed")],
                              default="draft", required=True, tracking=True)
