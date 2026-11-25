# fix_m48_routing — A07 ERP audit (2026-11-20): M48 alerts reach the module that
# owns the asset, and raise its work (spec §3.2 "M48 measures the generator; M47
# owns it and raises the work").
#
# - M48-15: iot.rule_alert_raised went to the IoT Operator only, and raised no
#   work. The alert is now addressed to the owning role (site -> Facility
#   Manager, equipment -> Equipment Custodian, vehicle -> Logistics Manager,
#   customer device / MSP endpoint -> IoT Operator for the account), and a major
#   or critical alert raises an inspection demand on the spine (once per alert;
#   a customer's device only when entitled, M48-04).
# - M48-18: iot.alert_raised (a device going offline or degraded) is routed the
#   same way; asset.alert_escalated (M48-10) reaches the owner too.
# - M48-13: asset.health_degraded into the degraded or critical band raises an
#   inspection demand (once per health row).
# - telemetry.model_suspended (BRU-IOT-22) reaches the IoT Manager.
# The statistical rule engine, hysteresis and correlation are deferred (D18).
from odoo import api, fields, models

from .fix_asset_alert import (
    CUSTODIAN,
    FACILITY,
    IOT_OPERATOR,
    LOGISTICS,
)
from .fix_maintenance_demand import _today

IOT_MANAGER = "cd_stream_registry.group_iot_manager"
# module -> the role that acts on its assets' alerts
OWNER_ROLE = {
    "M45": CUSTODIAN,
    "M46": LOGISTICS,
    "M47": FACILITY,
    "M17": IOT_OPERATOR,
    "M05": IOT_OPERATOR,
    "M48": IOT_OPERATOR,
}
ROUTED_TEXT = {
    "iot.rule_alert_raised": "A sensor rule raised an alert on your asset",
    "iot.alert_raised": "A monitoring device went offline or degraded",
    "asset.alert_escalated": "A sensor alert was not acknowledged within its SLA",
    "telemetry.model_suspended": "A prediction model was suspended from customer use",
}
INSPECT_SEVERITIES = ("major", "critical")
INSPECT_BANDS = ("degraded", "critical")


class FixAssetAlertOwner(models.Model):
    _inherit = "fix.asset.alert"

    @api.model
    def _fix_owner_route(self, event):
        """(module, role xmlid, text) for an M48 event, or None."""
        kind = event.get("event_type")
        if kind not in ROUTED_TEXT:
            return None
        if kind == "telemetry.model_suspended":
            return "M48", IOT_MANAGER, ROUTED_TEXT[kind]
        alert = self.env["fix.iot.alert"].sudo().browse(event.get("aggregate_id")).exists()
        module = (alert.routed_to_module or alert.device_id._fix_owner_module()) if alert else "M48"
        shown = module if module in dict(self._fields["module"].selection) else "M48"
        return shown, OWNER_ROLE.get(module, IOT_OPERATOR), ROUTED_TEXT[kind]

    @api.model
    def consume_asset_alert(self, event):
        """The M48 events go to the owner of the asset (the base table sends
        iot.rule_alert_raised to the IoT Operator). The row records the role it
        told (notified_groups), so only that role acknowledges it."""
        route = self._fix_owner_route(event)
        if not route:
            return super().consume_asset_alert(event)
        module, group_xmlid, text = route
        res_model = event.get("aggregate") or False
        res_id = event.get("aggregate_id") or 0
        now = fields.Datetime.now()
        Alert = self.sudo()
        record = (
            self.env[res_model].sudo().browse(res_id).exists()
            if res_model in self.env and res_id
            else False
        )
        label = record.display_name if record else "%s #%s" % (res_model or "", res_id)
        company = (
            event.get("company_id")
            or (record and "company_id" in record._fields and record.company_id.id)
            or self.env.company.id
        )
        existing = Alert.search(
            [
                ("event_type", "=", event["event_type"]),
                ("res_model", "=", res_model),
                ("res_id", "=", res_id),
                ("state", "=", "open"),
            ],
            limit=1,
        )
        if existing:
            existing.write({"raise_count": existing.raise_count + 1, "last_raised_on": now})
            return True
        holders = Alert._alert_holders([group_xmlid], company)
        alert = Alert.create(
            {
                "name": "%s: %s" % (text, label),
                "module": module,
                "event_type": event["event_type"],
                "res_model": res_model,
                "res_id": res_id,
                "record_label": label,
                "role_group": Alert._alert_role_label([group_xmlid]),
                "notified_groups": group_xmlid,
                "no_holder": not holders,
                "last_raised_on": now,
                "company_id": company,
            }
        )
        alert._alert_tell(holders, alert.name)
        return True


class FixMaintenanceDemandM48Routing(models.Model):
    _inherit = "fix.maintenance.demand"

    @api.model
    def _spine_m48_device_vals(self, device):
        """The demand's asset and route for work on an M48 device's asset."""
        device = device.sudo()
        customer = device._fix_customer_device()
        vals = {
            "company_id": device.company_id.id,
            "operating_unit_id": device.operating_unit_id.id,
            "work_type": "inspection",
            "equipment_id": device.equipment_id.id,
            "vehicle_id": device.vehicle_id.id,
            "iot_device_id": device.id,
            "site_id": device.site_id.id,
            "scheduled_date": _today(self.env),
            "entitlement_state": "internal",
            "commercial_route": "internal",
            "target": "work_order",
        }
        if device.vehicle_id:
            vals["branch_id"] = device.vehicle_id.branch_id.id
        elif customer or device.partner_id:
            vals.update(
                {
                    "target": "service_order",
                    "device_id": customer.id,
                    "partner_id": (customer.owner_id or device.partner_id).id,
                }
            )
            if customer:
                state, contract, _why = self._spine_entitlement(customer)
                vals.update(
                    {
                        "entitlement_state": state,
                        "commercial_route": "contract" if state == "entitled" else "opportunity",
                        "contract_ref_id": contract.id if contract else False,
                    }
                )
            else:
                vals.update({"entitlement_state": "no_contract", "commercial_route": "opportunity"})
        return vals

    @api.model
    def consume_iot_rule_alert_inspection(self, event):
        """iot.rule_alert_raised (major or critical) -> an inspection of the asset
        by its owner, once per alert (M48-15)."""
        alert = self.env["fix.iot.alert"].sudo().browse(event.get("aggregate_id")).exists()
        if not alert or alert.severity not in INSPECT_SEVERITIES or not alert.device_id:
            return False
        if self._spine_find(alert):
            return True
        device = alert.device_id
        vals = self._spine_m48_device_vals(device)
        vals["description"] = (
            "%s alert %s on %s (%s): %s. Inspect the monitored asset; the alert is closed in "
            "M48 by the IoT Operator."
            % (
                dict(alert._fields["severity"].selection).get(alert.severity),
                alert.name,
                device.name,
                device.device_id,
                alert.message,
            )
        )
        demand = self._spine_raise("m48_alert", alert, vals, label=alert.name)
        demand._spine_m48_opportunity()
        return True

    @api.model
    def consume_asset_health_degraded(self, event):
        """asset.health_degraded into the degraded or critical band -> an
        inspection of the asset, once per health row (M48-13)."""
        health = self.env["fix.iot.health"].sudo().browse(event.get("aggregate_id")).exists()
        if not health or health.band not in INSPECT_BANDS:
            return False
        if self._spine_find(health):
            return True
        device = health.device_id
        if not device:
            return False
        vals = self._spine_m48_device_vals(device)
        vals["work_type"] = "inspection"
        vals["description"] = (
            "Health index of %s (%s) fell to %s (%s, %s): %s. Inspect the asset."
            % (
                device.name,
                device.device_id,
                health.index_value,
                dict(health._fields["band"].selection).get(health.band),
                dict(health._fields["trend"].selection).get(health.trend),
                health.factors or "-",
            )
        )
        demand = self._spine_raise(
            "m48_health", health, vals, label="%s health %s" % (device.device_id, health.band)
        )
        demand._spine_m48_opportunity()
        return True
