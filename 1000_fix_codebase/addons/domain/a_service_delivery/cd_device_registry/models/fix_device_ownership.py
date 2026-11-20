# fix.device.ownership — ownership transfer record (P04-M01-T05).
from odoo import fields, models


class FixDeviceOwnership(models.Model):
    """An ownership transfer event — a permanent audit record."""
    _name = "fix.device.ownership"
    _description = "Device Ownership Transfer"
    # P03 workspace data-entry form (discovered by cd_p03_portal).
    _p03_capture = {
        "module": "M17",
        "form": "Ownership Transfer",
        "fields": ["device_id", "to_partner_id", "transfer_date", "transfer_type",
                   "from_partner_id", "notes"],
    }
    _inherit = ["mail.thread"]
    _order = "transfer_date desc"

    device_id = fields.Many2one("fix.device", string="Device", required=True,
                                ondelete="cascade", index=True)
    from_partner_id = fields.Many2one("res.partner", string="From")
    to_partner_id = fields.Many2one("res.partner", string="To", required=True)
    transfer_date = fields.Date(string="Transfer Date", default=fields.Date.today,
                                required=True)
    transfer_type = fields.Selection(
        [("sale", "Sale"), ("gift", "Gift"), ("return", "Return"),
         ("corporate", "Corporate Reallocation")],
        default="sale", required=True)
    notes = fields.Text()
