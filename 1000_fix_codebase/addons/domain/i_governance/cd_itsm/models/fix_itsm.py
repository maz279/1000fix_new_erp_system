# fix_itsm — M66: internal IT service management (P09-M08).
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish


class FixItsmTicket(models.Model):
    _name = "fix.itsm.ticket"
    _description = "ITSM Ticket"
    # P03 workspace data-entry form (discovered by cd_p03_portal).
    _p03_capture = {
        "module": "M66",
        "form": "Incident",
        "fields": ["title", "requester_id", "category", "priority", "description"],
    }
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, copy=False, readonly=True,
                       default=lambda self: "New")
    title = fields.Char(required=True)
    requester_id = fields.Many2one("hr.employee", string="Requester",
                                   required=True)
    category = fields.Selection(
        [("hardware", "Hardware"), ("software", "Software"),
         ("network", "Network"), ("account", "Account/Access"),
         ("other", "Other")], required=True, default="software")
    priority = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High"),
         ("urgent", "Urgent")], default="medium", required=True, tracking=True)
    state = fields.Selection(
        [("new", "New"), ("assigned", "Assigned"), ("in_progress", "In Progress"),
         ("resolved", "Resolved"), ("closed", "Closed")],
        default="new", required=True, tracking=True)
    assigned_to = fields.Many2one("hr.employee", string="Assigned To")
    description = fields.Text(required=True)
    resolution = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "fix.itsm.ticket") or "ITSM/New"
        recs = super().create(vals_list)
        for rec in recs:
            publish(self.env, "itsm.ticket_created", "fix.itsm.ticket",
                    rec.id, {"title": rec.title, "priority": rec.priority})
        return recs

    def action_resolve(self, resolution):
        for rec in self:
            if rec.state in ("resolved", "closed"):
                raise UserError("Ticket already resolved")
            rec.write({"state": "resolved", "resolution": resolution})
            publish(self.env, "itsm.ticket_resolved", "fix.itsm.ticket",
                    rec.id, {"ticket": rec.name})
