# fix.device.history service-order extension (P04-M01) — the order link.
# cd_device_registry sits BELOW cd_service_order in the module graph, so the
# history->order pointer is defined HERE, on the order side of the boundary
# (live-install finding: the inverse placement crashed registry load with
# "unknown comodel_name 'fix.service.order'").
from odoo import fields, models


class FixDeviceHistoryOrderExt(models.Model):
    _inherit = "fix.device.history"

    service_order_id = fields.Many2one("fix.service.order", string="Service Order",
                                       ondelete="set null")
