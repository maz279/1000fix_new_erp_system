# fix_spine_wiring — A07 P1 wiring (2026-11-04): the M45 / M47 / M48 events
# that FF-48 (check_deployment_wiring) found with no consumer, on the spine.
#
#   equipment.out_of_service      -> a calibration or repair demand per hold
#   equipment.returned_to_service -> that demand dismissed (pending) or noted
#   telemetry.stream_silent       -> an inspection demand per silence episode
#   facility.work_order_reopened  -> the demand back to routed, and said so
#
# Same rules as the rest of the spine: one demand per source item (the hold,
# the gap), routed when the facts on file allow it, otherwise left pending
# with what it needs. Nothing here resolves an M45 hold, reactivates an M48
# stream or un-completes a source record: those stay with their owners.
from odoo import api, models

from .fix_maintenance_demand import WO_MODEL, _today

HOLD_LABELS = {
    "calibration": "re-calibrate it and record the passing calibration in M45",
    "fault": "repair the fault",
    "damaged": "repair the damage",
    "inspection": "carry out the condition check",
}


class FixMaintenanceDemandWiring(models.Model):
    _inherit = "fix.maintenance.demand"

    # ------------------------------------------------------------ M45 holds
    @api.model
    def consume_equipment_out_of_service(self, event):
        """equipment.out_of_service -> the work that returns the instrument to
        service: a calibration demand for a calibration hold, a repair (or
        condition-check) demand otherwise. Idempotent per hold."""
        hold = self.env["fix.equipment.oos"].sudo().browse(event.get("aggregate_id")).exists()
        if not hold or hold.state != "open":
            return False
        if self._spine_find(hold):
            return True
        equipment = hold.equipment_id
        calibration = hold.hold_type == "calibration"
        vals = {
            "company_id": equipment.company_id.id or self.env.company.id,
            "operating_unit_id": equipment.operating_unit_id.id,
            "target": "work_order",
            "work_type": "inspection"
            if hold.hold_type in ("calibration", "inspection")
            else "repair",
            "equipment_id": equipment.id,
            "branch_id": equipment.branch_id.id,
            "technician_id": equipment.custodian_id.id,
            "scheduled_date": _today(self.env),
            "calibration_due": hold.started_on if calibration else False,
            "description": "%s (%s) is out of service under hold %s since %s (%s: %s): %s. "
            "The hold is returned to service in M45 by the Quality Manager (a store keeper "
            "for a condition check); this work order does not stand in for it."
            % (
                equipment.name,
                equipment.code,
                hold.name,
                hold.started_on,
                dict(hold._fields["hold_type"].selection).get(hold.hold_type),
                hold.reason,
                HOLD_LABELS.get(hold.hold_type, "repair it"),
            ),
        }
        self._spine_raise(
            "m45_calibration" if calibration else "m45_repair",
            hold,
            vals,
            label="%s %s" % (equipment.code, hold.name),
        )
        return True

    @api.model
    def consume_equipment_returned_to_service(self, event):
        """equipment.returned_to_service -> the hold's demand: dismissed with
        the reason while it is still pending; a routed work order is left to
        its Facility Manager (completed or cancelled there) and told."""
        hold = self.env["fix.equipment.oos"].sudo().browse(event.get("aggregate_id")).exists()
        if not hold:
            return False
        demand = self._spine_find(hold)
        if not demand:
            return True  # the hold raised no work
        payload = event.get("payload") or {}
        how = (
            "re-calibration %s accepted" % hold.resolution_calibration_id.display_name
            if hold.resolution_calibration_id
            else "condition check passed"
        )
        reason = "%s returned to service on %s (%s), status %s" % (
            hold.name,
            payload.get("effective_from") or hold.resolved_on or "-",
            how,
            payload.get("status") or hold.equipment_id.operational_status,
        )
        marker = "rts:%s" % hold.id
        if "[%s]" % marker in (demand.source_log or ""):
            return True
        if demand.state == "pending":
            demand.action_dismiss(reason="M45: %s." % reason)
            demand._spine_log(marker, "M45 %s: demand dismissed." % reason)
            return True
        wo = demand.work_order_id
        if demand.state == "routed" and wo and wo.state in ("draft", "scheduled", "in_progress"):
            text = (
                "M45 %s. Work order %s is %s and stays as it is: its Facility Manager "
                "completes it, or cancels it if no work is left." % (reason, wo.name, wo.state)
            )
            wo.message_post(body=text)
        else:
            text = "M45 %s." % reason
        demand._spine_log(marker, text)
        return True

    # ------------------------------------------------------------ M48 silence
    @api.model
    def consume_telemetry_stream_silent(self, event):
        """telemetry.stream_silent -> an inspection of the device's asset: the
        internal asset's spine work order, or a DRAFT M01 order for a
        customer-premises device (routed as the spine routes M48 demands).
        Idempotent per silence episode (the gap); a second stream of the same
        device falling silent while its inspection is open joins it."""
        stream = self.env["fix.iot.stream"].sudo().browse(event.get("aggregate_id")).exists()
        if not stream:
            return False
        payload = event.get("payload") or {}
        Gap = self.env["fix.iot.gap"].sudo()
        gap = Gap.search(
            [("stream_id", "=", stream.id), ("name", "=", payload.get("gap") or "")], limit=1
        ) or Gap.search([("stream_id", "=", stream.id), ("state", "=", "open")], limit=1)
        if not gap:
            return False
        device = stream.device_id
        marker = "gap:%s" % gap.id
        mine = self.sudo().search(
            [("iot_device_id", "=", device.id), ("origin", "=", "m48_silent")]
        )
        if self._spine_find(gap) or any("[%s]" % marker in (d.source_log or "") for d in mine):
            return True  # this episode is on a demand already
        what = "stream %s (%s) silent since %s (gap %s, %s)" % (
            stream.name,
            stream.metric,
            payload.get("last_point") or gap.gap_from,
            gap.name,
            "had readings" if gap.had_reading else "never reported",
        )
        host = mine.filtered(lambda d: d.state == "pending" or d._spine_target_open())
        if host:
            host[0]._spine_log(marker, "Also %s." % what)
            return True
        equipment = device.equipment_id
        vals = {
            "company_id": device.company_id.id,
            "operating_unit_id": device.operating_unit_id.id,
            "target": "service_order" if device.partner_id else "work_order",
            "work_type": "inspection",
            "equipment_id": equipment.id,
            "iot_device_id": device.id,
            "site_id": device.site_id.id,
            "partner_id": device.partner_id.id,
            "scheduled_date": _today(self.env),
            "description": "IoT device %s (%s) stopped reporting: %s. Inspect the device, its "
            "power and its connection%s. The missed readings are a gap, never zeros."
            % (
                device.name,
                device.device_id,
                what,
                " and the monitored %s (%s)" % (equipment.name, equipment.code)
                if equipment
                else "",
            ),
        }
        demand = self._spine_raise(
            "m48_silent", gap, vals, label="%s silent (%s)" % (device.device_id, gap.name)
        )
        demand._spine_log(marker, "Raised for %s." % what)
        return True

    # ------------------------------------------------------------ M47 reopen
    @api.model
    def consume_facility_work_order_reopened(self, event):
        """facility.work_order_reopened -> a reopened spine work order puts its
        demand back to routed (the work is open again). A source already
        completed is NOT un-completed: the demand says so, for the Facility
        Manager to re-check it. Idempotent per event."""
        wo = self.env[WO_MODEL].sudo().browse(event.get("aggregate_id")).exists()
        if not wo:
            return False
        demands = (wo.spine_demand_id | self.sudo().search([("work_order_id", "=", wo.id)])).sudo()
        if not demands:
            return True  # not a spine work order
        payload = event.get("payload") or {}
        marker = "reopen:%s" % (event.get("event_id") or wo.id)
        done = []
        for source, label in (
            (wo.pm_id, "M47 PM"),
            (wo.equipment_pm_id, "M45 job"),
            (wo.vehicle_pm_id, "M46 service"),
        ):
            if source and source.sudo().state == "done":
                done.append("%s %s" % (label, source.sudo().name))
        action = wo.iot_action_id.sudo()
        if action and action.state == "done":
            done.append("M48 action %s (outcome %s)" % (action.name, action.outcome or "-"))
        if wo.spine_calibration_id:
            done.append("calibration %s" % wo.spine_calibration_id.display_name)
        for demand in demands:
            if "[%s]" % marker in (demand.source_log or ""):
                continue
            parts = [
                "Work order %s reopened: %s."
                % (wo.name, payload.get("reason") or "no reason given")
            ]
            if demand.state == "done":
                demand._guarded().write({"state": "routed"})
                parts.append("The demand is routed again.")
            if done:
                parts.append(
                    "Already completed at the source: %s. It is not un-completed: re-check it "
                    "against the reopened work." % ", ".join(done)
                )
            demand._spine_log(marker, " ".join(parts))
        return True
