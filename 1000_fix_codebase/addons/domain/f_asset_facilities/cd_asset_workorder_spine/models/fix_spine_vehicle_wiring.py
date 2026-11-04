# fix_spine_vehicle_wiring — A07 P1 wiring round 2 (2026-11-04): the M46
# vehicle events FF-48 found with no consumer, on the spine.
#
#   vehicle.defect_raised     -> a repair demand per failed pre-use check
#   vehicle.telematics_silent -> an inspection demand per silence episode of
#                                the vehicle's telematics device
#
# M46 took the van off the road on the failed check and marked the snapshot
# stale, then nobody was asked to repair or inspect anything. Same rules as
# the rest of the spine: one demand per source item (the check, the
# snapshot), routed to the M47 work order of the vehicle's branch site when
# the facts allow it, else pending with what it needs; a second failure of
# the same vehicle (device) while its work is open joins that demand instead
# of raising another. Nothing here returns a van to service: that stays a
# Fleet Officer's, on a passed re-check (M46).
from odoo import api, models

from .fix_maintenance_demand import NO_KEY, WO_MODEL, _today


def _plate(vehicle):
    vehicle = vehicle.sudo()
    return vehicle.name or vehicle.license_plate or ""


class FixMaintenanceDemandVehicleWiring(models.Model):
    _inherit = "fix.maintenance.demand"

    @api.model
    def _spine_vehicle_vals(self, vehicle, work_type, description):
        vehicle = vehicle.sudo()
        return {
            "company_id": vehicle.company_id.id or self.env.company.id,
            "operating_unit_id": vehicle.operating_unit_id.id,
            "target": "work_order",
            "work_type": work_type,
            "vehicle_id": vehicle.id,
            "branch_id": vehicle.branch_id.id,
            "scheduled_date": _today(self.env),
            "description": description,
        }

    @api.model
    def _spine_vehicle_host(self, vehicle, origin, key=NO_KEY):
        """The vehicle's open demand of this origin (pending, or routed with
        its work order still open)."""
        return (
            self.sudo()
            .search(
                [
                    ("vehicle_id", "=", vehicle.id),
                    ("origin", "=", origin),
                    ("source_key", "=", key or NO_KEY),
                    ("state", "in", ("pending", "routed")),
                ],
                order="id asc",
            )
            .filtered(lambda d: d.state == "pending" or d._spine_target_open())
        )

    # ------------------------------------------------------------ defect
    @api.model
    def consume_vehicle_defect_raised(self, event):
        """vehicle.defect_raised -> the repair of the defect a failed pre-use
        check found: one demand per check; a further failed check of the same
        vehicle while that repair is open is logged on it. Idempotent per
        check."""
        check = self.env["fix.vehicle.check"].sudo().browse(event.get("aggregate_id")).exists()
        if not check or check.passed:
            return False
        payload = event.get("payload") or {}
        vehicle = check.vehicle_id
        marker = "check:%s" % check.id
        mine = self.sudo().search([("vehicle_id", "=", vehicle.id), ("origin", "=", "m46_defect")])
        if self._spine_find(check) or any("[%s]" % marker in (d.source_log or "") for d in mine):
            return True  # this check is on a demand already
        offroad = (
            self.env["fix.vehicle.offroad"].sudo().search([("check_id", "=", check.id)], limit=1)
        )
        what = "pre-use check %s of %s failed (%s)%s" % (
            check.name,
            check.checked_on,
            payload.get("defect") or check.defects or "-",
            ", safety-critical" if payload.get("safety_critical") else "",
        )
        host = self._spine_vehicle_host(vehicle, "m46_defect")
        if host:
            host[0]._spine_log(marker, "Also %s." % what)
            return True
        description = (
            "Vehicle %s: %s%s. Repair the defect. The vehicle returns to service in M46 only "
            "on a passed pre-use check, by a Fleet Officer other than the one who took it off "
            "the road: this work order does not stand in for it."
            % (
                _plate(vehicle),
                what,
                "; off-road record %s" % offroad.name if offroad else "",
            )
        )
        demand = self._spine_raise(
            "m46_defect",
            check,
            self._spine_vehicle_vals(vehicle, "repair", description),
            label="%s defect (%s)" % (_plate(vehicle), check.name),
        )
        demand._spine_log(marker, "Raised for %s." % what)
        return True

    # ------------------------------------------------------------ telematics
    @api.model
    def consume_vehicle_telematics_silent(self, event):
        """vehicle.telematics_silent -> an inspection of the vehicle's
        telematics device. Idempotent per silence episode (the stale snapshot);
        a later episode of the same device while its inspection is open joins
        it, and a device that reported again before the event was relayed
        raises nothing."""
        Tel = self.env["fix.vehicle.telemetry"].sudo()
        snap = Tel.browse(event.get("aggregate_id")).exists()
        if not snap or snap.state == "online":
            return False
        payload = event.get("payload") or {}
        vehicle = snap.vehicle_id
        device = snap.device_ref or payload.get("device") or ""
        key = device or NO_KEY
        if Tel.search_count(
            [
                ("vehicle_id", "=", vehicle.id),
                ("device_ref", "=", snap.device_ref or False),
                ("id", ">", snap.id),
                ("state", "=", "online"),
            ]
        ):
            return True  # the device reported again: no episode left to inspect
        marker = "telemetry:%s" % snap.id
        mine = self.sudo().search(
            [
                ("vehicle_id", "=", vehicle.id),
                ("origin", "=", "m46_telematics"),
                ("source_key", "=", key),
            ]
        )
        if self._spine_find(snap, key) or any(
            "[%s]" % marker in (d.source_log or "") for d in mine
        ):
            return True
        what = "telematics device %s silent since %s (snapshot %s)" % (
            device or "(no reference)",
            payload.get("last_report") or snap.last_ping or "it never reported",
            snap.name,
        )
        host = self._spine_vehicle_host(vehicle, "m46_telematics", key)
        if host:
            host[0]._spine_log(marker, "Again %s." % what)
            return True
        description = (
            "Vehicle %s: %s. Inspect the device, its power, SIM and mounting. Until it "
            "reports, M02 does not know where the vehicle is; the missed positions are a "
            "gap, never a location." % (_plate(vehicle), what)
        )
        demand = self._spine_raise(
            "m46_telematics",
            snap,
            self._spine_vehicle_vals(vehicle, "inspection", description),
            key=key,
            label="%s telematics %s silent (%s)" % (_plate(vehicle), device or "-", snap.name),
        )
        demand._spine_log(marker, "Raised for %s." % what)
        return True


class FixFacilityWorkOrderVehicleWiring(models.Model):
    _inherit = WO_MODEL

    def _spine_complete_source(self):
        """A verified defect repair does not return the van to service: the
        work order says which M46 off-road record still holds it."""
        res = super()._spine_complete_source()
        Off = self.env["fix.vehicle.offroad"].sudo()
        for rec in self.filtered(lambda w: w.spine_origin == "m46_defect" and w.vehicle_id):
            off = Off.search(
                [("vehicle_id", "=", rec.vehicle_id.id), ("state", "=", "offroad")], limit=1
            )
            if off:
                rec.message_post(
                    body="Vehicle %s stays off the road under %s until a Fleet Officer "
                    "returns it in M46 on a passed pre-use check."
                    % (_plate(rec.vehicle_id), off.name)
                )
        return res
