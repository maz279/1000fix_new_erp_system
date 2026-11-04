# m49_transfer — A07 P1 (2026-11-04), report §6 P1 "Event consumers": an M45
# equipment transfer reaches the M49 register (spec §10.2 "transfer trigger").
#
# Before: a received M45 transfer moved the instrument's branch and custodian,
# and the capitalised asset stayed booked at the old branch under the old
# custodian, so depreciation landed on the wrong branch dimension. Now a
# received transfer of a CAPITALISED item raises ONE draft fix.asset.transfer
# (M49's own record), which an accountant confirms with M49's Confirm. The
# bridge never confirms it: confirming moves the asset, and that is finance's.
from odoo import api, fields, models
from odoo.exceptions import UserError

from .fix_bridge_exception import event_source, noted, source_key


class FixAssetTransferBridge(models.Model):
    _inherit = "fix.asset.transfer"

    equipment_transfer_id = fields.Many2one(
        "fix.equipment.transfer",
        string="M45 Transfer",
        readonly=True,
        copy=False,
        index=True,
        help="The received M45 equipment transfer this draft was raised from",
    )

    _equipment_transfer_unique = models.Constraint(
        "UNIQUE (equipment_transfer_id)", "One M49 transfer per M45 equipment transfer."
    )

    def write(self, vals):
        if not self.env.su and "equipment_transfer_id" in vals:
            raise UserError("The M45 link of an asset transfer is set by the bridge only.")
        return super().write(vals)

    @api.model
    def consume_equipment_transferred(self, event):
        """equipment.transferred (M45 receipt confirmed) -> a DRAFT M49 transfer
        of the item's fixed asset to the receiving branch and custodian.
        Idempotent per M45 transfer. Not capitalised: a pending capitalisation
        request follows the item to its new branch instead."""
        move = event_source(self.env, event, "fix.equipment.transfer")
        if not move or move.state != "received":
            return False
        existing = self.sudo().search([("equipment_transfer_id", "=", move.id)], limit=1)
        if existing:
            return existing
        equipment = move.equipment_id.sudo()
        to_ou = move.to_branch_id.operating_unit_id
        what = "M45 transfer %s of %s received at %s on %s" % (
            move.name,
            equipment.code,
            move.to_branch_id.name or "-",
            move.received_on or "-",
        )
        asset = equipment.fixed_asset_id
        if not asset:
            Req = self.env["fix.asset.finance.request"].sudo()
            req = Req.search(
                [("key", "=", source_key("m49:capitalise", equipment)), ("state", "=", "pending")],
                limit=1,
            )
            if req and to_ou and req.operating_unit_id != to_ou:
                req.write({"operating_unit_id": to_ou.id})
                req.message_post(body="%s: the pending request now names that branch." % what)
            return req
        if asset.state != "active":
            if not noted(asset, what):
                asset.message_post(
                    body="%s. The asset is %s in M49: finance updates its branch and custodian "
                    "before putting it into service." % (what, asset.state)
                )
            return self.browse()
        target_ou = to_ou or asset.operating_unit_id
        target_custodian = move.to_custodian_id or asset.custodian_id
        if target_ou == asset.operating_unit_id and target_custodian == asset.custodian_id:
            return self.browse()  # the register already shows where the item is
        transfer = self.sudo().create(
            {
                "asset_id": asset.id,
                "date": move.received_on or fields.Date.context_today(self),
                "operating_unit_id": target_ou.id,
                "to_custodian_id": target_custodian.id,
                "reason": "%s (from %s, custodian %s). Raised by the asset bridge: confirm "
                "it in M49 to move the asset."
                % (
                    what,
                    move.from_branch_id.name or "-",
                    move.from_custodian_id.name or "-",
                ),
                "equipment_transfer_id": move.id,
            }
        )
        transfer.message_post(body="Draft raised from %s. Finance confirms it." % what)
        return transfer
