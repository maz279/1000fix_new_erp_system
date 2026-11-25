# fix.device.history — permanent device service history (P04-M01-T07).
# Every service order against a device, permanently.
from odoo import api, fields, models
from odoo.exceptions import UserError


class FixDeviceHistory(models.Model):
    """A permanent history entry for a device — never deleted."""

    _name = "fix.device.history"
    _description = "Device History"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "date desc"
    _log_access = True

    @api.model_create_multi
    def create(self, vals_list):
        # A07 audit (2026-11-04) M17-7 / AUT-AST-05: history is projected from
        # the transactions that touch the device (fix.device.add_history, used
        # by M01 and the registry), never typed. A plain user fabricated
        # back-dated "repair" rows with no order, which put the device on the
        # Repeat-Fault Pareto. Edit and delete were already refused (ACL).
        if not self._fix_guard_open():
            raise UserError(
                "Device history is projected from service orders and registry events "
                "and cannot be entered by hand."
            )
        return super().create(vals_list)

    device_id = fields.Many2one(
        "fix.device", string="Device", required=True, ondelete="restrict", index=True
    )
    date = fields.Datetime(string="Date", required=True, index=True)
    event_type = fields.Selection(
        [
            ("registered", "Registered"),
            ("service_order", "Service Order"),
            ("repair", "Repair"),
            ("transfer", "Ownership Transfer"),
            ("warranty", "Warranty Update"),
            ("qc", "Quality Check"),
            ("return", "Return"),
            ("other", "Other"),
        ],
        required=True,
        index=True,
    )
    description = fields.Text(required=True)
    # service_order_id lives in cd_service_order (fix_device_history_ext):
    # cd_service_order depends on cd_device_registry, so the inverse pointer
    # must be defined on the ORDER side of the boundary (live-install finding).
    branch_id = fields.Many2one("fix.branch", string="Branch")
    technician_id = fields.Many2one("hr.employee", string="Technician")
