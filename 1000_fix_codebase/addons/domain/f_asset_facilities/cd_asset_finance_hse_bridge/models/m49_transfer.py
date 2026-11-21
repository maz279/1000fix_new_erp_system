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
from odoo.addons.cd_fixed_asset_ext.models.fix_asset_common import (
    money,
    post_entry,
    require_accounts,
)
from odoo.exceptions import UserError

from .fix_bridge_exception import dhaka_today, event_source, noted, run_hook, source_key


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

    vehicle_id = fields.Many2one(
        "fleet.vehicle", string="M46 Vehicle", readonly=True, copy=False, index=True
    )
    gl_move_id = fields.Many2one(
        "account.move", string="Branch Reclass Entry", readonly=True, copy=False
    )

    _equipment_transfer_unique = models.Constraint(
        "UNIQUE (equipment_transfer_id)", "One M49 transfer per M45 equipment transfer."
    )

    def write(self, vals):
        if not self.env.su and {"equipment_transfer_id", "vehicle_id", "gl_move_id"} & set(vals):
            raise UserError("The source link of an asset transfer is set by the bridge only.")
        return super().write(vals)

    def action_acknowledge(self):
        """A07 FIN-13: the asset's cost and accumulated depreciation move with
        it in the GL. When the branch changes, the acknowledgement posts the
        reclass: Dr cost / Cr accumulated depreciation on the receiving branch,
        Cr cost / Dr accumulated depreciation on the sending one."""
        before = {rec.id: rec.asset_id.operating_unit_id for rec in self}
        result = super().action_acknowledge()
        for rec in self.filtered(lambda t: t.state == "done"):
            from_ou, to_ou = before[rec.id], rec.asset_id.operating_unit_id
            if from_ou and to_ou and from_ou != to_ou:
                rec._bridge_post_reclass(from_ou, to_ou)
        return result

    def _bridge_post_reclass(self, from_ou, to_ou):
        self.ensure_one()
        asset = self.asset_id.sudo()
        cat = asset.category_id
        cost = money(asset.cost)
        accumulated = money(asset.accumulated_depreciation + asset.impairment_total)
        if not cost and not accumulated:
            return self.env["account.move"]
        needed = ["journal_id", "asset_account_id"]
        if accumulated:
            needed.append("accumulated_account_id")
        require_accounts(cat, needed, "The branch transfer of %s" % asset.display_name)
        label = "%s %s: %s -> %s" % (self.name, asset.display_name, from_ou.name, to_ou.name)
        lines = [
            (cat.asset_account_id, cost, 0.0, label, to_ou),
            (cat.asset_account_id, 0.0, cost, label, from_ou),
        ]
        if accumulated:
            lines += [
                (cat.accumulated_account_id, accumulated, 0.0, label, from_ou),
                (cat.accumulated_account_id, 0.0, accumulated, label, to_ou),
            ]
        move = post_entry(
            self.env,
            asset.company_id,
            cat.journal_id,
            min(self.date or dhaka_today(self.env), dhaka_today(self.env)),
            label,
            lines,
        )
        self.sudo()._guarded().write({"gl_move_id": move.id})
        return move

    @api.model
    def _bridge_vehicle_moved(self, vehicles):
        """FIN-13: a capitalised vehicle moved to another branch raises ONE
        draft M49 transfer to that branch, which finance confirms."""
        for v in vehicles.sudo():
            asset = v.fixed_asset_id
            to_ou = v.operating_unit_id or v.branch_id.operating_unit_id
            if not asset or asset.state != "active" or not to_ou:
                continue
            if asset.operating_unit_id == to_ou:
                continue
            open_ = self.sudo().search(
                [("vehicle_id", "=", v.id), ("state", "in", ("draft", "confirmed"))], limit=1
            )
            if open_:
                if open_.state == "draft" and open_.operating_unit_id != to_ou:
                    open_.write({"operating_unit_id": to_ou.id})
                continue
            transfer = self.sudo().create(
                {
                    "asset_id": asset.id,
                    "date": dhaka_today(self.env),
                    "operating_unit_id": to_ou.id,
                    "to_custodian_id": asset.custodian_id.id,
                    "reason": "Vehicle %s moved to %s in M46. Raised by the asset bridge: "
                    "confirm it in M49 to move the asset and its GL balances."
                    % (v.license_plate or v.name, to_ou.name),
                    "vehicle_id": v.id,
                }
            )
            transfer.message_post(body="Draft raised from the M46 branch change.")

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


class FleetVehicleM49Transfer(models.Model):
    _inherit = "fleet.vehicle"

    def write(self, vals):
        result = super().write(vals)
        if {"operating_unit_id", "branch_id"} & set(vals):
            Transfer = self.env["fix.asset.transfer"].sudo()
            run_hook(self.env, "m49_vehicle_transfer", Transfer._bridge_vehicle_moved, self)
        return result


class FixAssetDisposalVehicle(models.Model):
    _inherit = "fix.asset.disposal"

    def _bridge_vehicle(self):
        self.ensure_one()
        if not self.asset_id:
            return self.env["fleet.vehicle"]
        return (
            self.env["fleet.vehicle"]
            .sudo()
            .with_context(active_test=False)
            .search([("fixed_asset_id", "=", self.asset_id.id)], limit=1)
        )

    def _dofa_thresholds(self):
        """D10 / BRU-FLT-20: the disposal of a vehicle is the CFO's (DOFA tier 4)
        whatever its amount."""
        if len(self) == 1 and self._bridge_vehicle():
            return [(-1.0, "tier_0"), (float("inf"), "tier_4")]
        return super()._dofa_thresholds()
