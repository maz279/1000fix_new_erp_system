# fix.device.history — permanent device service history (P04-M01-T07).
# Every service order against a device, permanently.
from odoo import fields, models


class FixDeviceHistory(models.Model):
    """A permanent history entry for a device — never deleted."""
    _name = "fix.device.history"
    _description = "Device History"
    _order = "date desc"
    _log_access = True

    device_id = fields.Many2one("fix.device", string="Device", required=True,
                                ondelete="restrict", index=True)
    date = fields.Datetime(string="Date", required=True, index=True)
    event_type = fields.Selection(
        [("registered", "Registered"), ("service_order", "Service Order"),
         ("repair", "Repair"), ("transfer", "Ownership Transfer"),
         ("warranty", "Warranty Update"), ("qc", "Quality Check"),
         ("return", "Return"), ("other", "Other")],
        required=True, index=True)
    description = fields.Text(required=True)
    service_order_id = fields.Many2one("fix.service.order", string="Service Order",
                                        ondelete="set null")
    branch_id = fields.Many2one("fix.branch", string="Branch")
    technician_id = fields.Many2one("hr.employee", string="Technician")
