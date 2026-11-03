# fix.device.ownership — ownership transfer record (P04-M01-T05).
from odoo import api, fields, models
from odoo.exceptions import UserError


class FixDeviceOwnership(models.Model):
    """An ownership transfer event — a permanent audit record.

    BRU-AST-06: ownership history is never overwritten or deleted. A07 audit
    (2026-11-03) M17-1: plain users could rewrite a row, or create one that
    contradicted the device's owner. Rows are now written only by
    ``fix.device.action_transfer_ownership`` (guard token) or superuser code."""

    _name = "fix.device.ownership"
    _description = "Device Ownership Transfer"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "transfer_date desc"

    def _fix_refuse_unless_transfer(self):
        if not self._fix_guard_open():
            raise UserError(
                "Ownership history is a permanent record. A row is written only by an "
                "ownership transfer on the device, and is never edited or deleted."
            )

    @api.model_create_multi
    def create(self, vals_list):
        self._fix_refuse_unless_transfer()
        return super().create(vals_list)

    def write(self, vals):
        # mail.thread writes its own bookkeeping (followers, message counters).
        if set(vals) - {"message_follower_ids", "message_main_attachment_id"}:
            self._fix_refuse_unless_transfer()
        return super().write(vals)

    def unlink(self):
        self._fix_refuse_unless_transfer()
        return super().unlink()

    device_id = fields.Many2one(
        "fix.device", string="Device", required=True, ondelete="cascade", index=True
    )
    from_partner_id = fields.Many2one("res.partner", string="From")
    to_partner_id = fields.Many2one("res.partner", string="To", required=True)
    transfer_date = fields.Date(string="Transfer Date", default=fields.Date.today, required=True)
    transfer_type = fields.Selection(
        [
            ("sale", "Sale"),
            ("gift", "Gift"),
            ("return", "Return"),
            ("corporate", "Corporate Reallocation"),
        ],
        default="sale",
        required=True,
    )
    notes = fields.Text()
