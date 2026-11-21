# fix_exit_asset_clearance — A07 P1 bridge: M21 exit clearance against the
# assets the leaver still holds (BRU-EAM-09 / AC-12, M46 BRU-FLT-06).
#
# A07 audit (2026-11-03) probe m45_32: an exit was cleared with every box
# ticked while an M45 equipment issue to the leaver was still open; the
# clearance read the ticked boxes and employee.toolkit_custody_ref only. It
# now also reads the registers: open equipment custody (M45), duty bookings
# from today on where the leaver drives or is the technician (M46), and
# vehicles on which the leaver is the assigned driver. The message names each.
from odoo import fields, models
from odoo.exceptions import UserError


class FixHrExitAssetClearance(models.Model):
    _inherit = "fix.hr.exit"

    def _spine_assets_held(self):
        """What the leaver still holds, one line per item (read as superuser:
        HR clears against every branch's register, not the rows it can see)."""
        self.ensure_one()
        employee = self.employee_id
        if not employee:
            return []
        env = self.env(su=True)
        held = []
        open_issues = env["fix.equipment.issue"].m45_open_custody_for_employee(employee)
        for issue in open_issues:
            held.append(
                "equipment %s %s (issue %s since %s)"
                % (issue.equipment_id.code, issue.equipment_id.name, issue.name, issue.issued_on)
            )
        # A07 ERP audit (2026-11-20) M45-10 / BRU-EAM-09, FR-EAM-012: the
        # register custodian (a store keeper's or technician's personal kit not
        # out on an issue row) is accountable too, until a received transfer
        # names someone else.
        registered = (
            env["fix.equipment"]
            .with_context(active_test=False)
            .search(
                [
                    ("custodian_id", "=", employee.id),
                    ("operational_status", "!=", "retired"),
                    ("id", "not in", open_issues.equipment_id.ids),
                ],
                order="code",
            )
        )
        for item in registered:
            held.append(
                "equipment %s %s (register custodian; transfer it to another custodian)"
                % (item.code, item.name)
            )
        today = fields.Date.context_today(self.with_context(tz="Asia/Dhaka"))
        drivers = (
            env["fix.driver"]
            .with_context(active_test=False)
            .search([("employee_id", "=", employee.id)])
        )
        bookings = env["fix.vehicle.assignment"].search(
            [
                ("date", ">=", today),
                "|",
                ("technician_id", "=", employee.id),
                ("driver_id", "in", drivers.ids),
            ],
            order="date",
        )
        for booking in bookings:
            vehicle = booking.vehicle_id
            role = "driver" if booking.driver_id in drivers else "technician"
            held.append(
                "vehicle assignment of %s on %s (as %s)"
                % (vehicle.name or vehicle.license_plate or "vehicle", booking.date, role)
            )
        Vehicle = env["fleet.vehicle"]
        domain = [("fix_driver_id", "in", drivers.ids)]
        if "driver_employee_id" in Vehicle._fields:
            domain = ["|", ("driver_employee_id", "=", employee.id), *domain]
        for vehicle in Vehicle.search(domain):
            held.append(
                "assigned driver of vehicle %s" % (vehicle.name or vehicle.license_plate or "")
            )
        # R2a (2026-11-21), D9/D20: an HR-approved recharge (lost or damaged
        # equipment, a recovered fine or excess) booked on 100049 and not yet
        # collected is settled before the leaver goes, never left on the books.
        if "fix.asset.recovery" in env:
            recoveries = env["fix.asset.recovery"].search(
                [
                    ("kind", "=", "employee"),
                    ("employee_id", "=", employee.id),
                    ("state", "in", ("approved", "in_payroll")),
                ],
                order="id",
            )
            for recovery in recoveries:
                owed = recovery._recovery_outstanding()
                if owed > 0.005:
                    held.append(
                        "recovery %s of %.2f still owed (%s; settle it in the final "
                        "settlement)" % (recovery.name, owed, recovery.source_ref or "-")
                    )
        return held

    def action_clear(self):
        # action_clear accepts a confirmed exit ("notice"); the gate filtered
        # on "draft" and so never ran (M21 audit E5).
        for rec in self.filtered(lambda r: r.state in ("draft", "notice")):
            held = rec._spine_assets_held()
            if held:
                raise UserError(
                    "Exit %s of %s cannot be cleared while company assets are still in the "
                    "employee's hands: %s. Return the equipment, reassign the bookings and "
                    "the vehicles first (BRU-EAM-09)."
                    % (rec.name, rec.employee_id.name, "; ".join(held))
                )
        return super().action_clear()
