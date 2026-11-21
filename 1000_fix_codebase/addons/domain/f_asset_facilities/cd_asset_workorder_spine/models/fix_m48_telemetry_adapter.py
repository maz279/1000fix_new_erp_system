# fix_m48_telemetry_adapter — A07 ERP audit (2026-11-20) M48-06 / decision D17(a):
# M48 is the single time-series store. The M46 telematics snapshots and the M05
# RMM endpoint readings keep their business objects, and every reading of a
# vehicle or endpoint REGISTERED IN M48 (fix.iot.device.vehicle_id /
# monitored_asset_id) is fed through the M48 stream ingest, so the consent gate,
# the duplicate check, the rules and retention apply to it.
#
# The consent gate is applied, not bypassed: when it refuses (no valid consent,
# or a signal the consent does not disclose) the M46 snapshot / M05 reading is
# refused with it - collection stops. Any other refusal (an adapter switched
# off, a replayed reading) is logged and the source's own record stands.
#
# Mapping: a stream's metric names what it carries -
#   M46: odometer_km <- odometer, fuel_level_pct <- fuel_level_pct
#   M05: endpoint_health (0 healthy / 1 degraded / 2 offline), cpu_utilization_pct,
#        ram_utilization_pct, disk_free_gb, uptime_hours
# The external AEMP / ISO 15143-3 adapter is deferred (D18).
import logging

from odoo import api, models
from odoo.addons.cd_stream_registry.models.fix_iot_ops import IngestRefused
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

CONSENT_CODES = ("consent_required", "signal_not_disclosed")
VEHICLE_METRICS = {"odometer_km": "odometer", "fuel_level_pct": "fuel_level_pct"}
ENDPOINT_HEALTH = {"healthy": 0.0, "degraded": 1.0, "offline": 2.0}
ENDPOINT_METRICS = {
    "cpu_utilization_pct": "cpu_utilization_pct",
    "ram_utilization_pct": "ram_utilization_pct",
    "disk_free_gb": "disk_free_gb",
    "uptime_hours": "uptime_hours",
}


def _feed(streams, values, stamp, source):
    """Ingest {metric: value} on the matching live streams. A consent refusal
    propagates (collection stops); anything else is logged."""
    fed = 0
    for stream in streams:
        if stream.metric not in values or values[stream.metric] is None:
            continue
        try:
            with stream.env.cr.savepoint():
                stream.sudo().ingest(values[stream.metric], timestamp=stamp)
            fed += 1
        except IngestRefused as exc:
            if exc.code in CONSENT_CODES:
                raise
            _logger.info("M48 adapter: %s not fed to %s (%s)", source, stream.name, exc.code)
        except ValidationError as exc:
            _logger.info("M48 adapter: %s not fed to %s (%s)", source, stream.name, exc)
    return fed


def _live_streams(env, devices):
    return (
        env["fix.iot.stream"]
        .sudo()
        .search([("device_id", "in", devices.ids), ("state", "in", ("active", "silent"))])
    )


class FixVehicleTelemetryM48(models.Model):
    _inherit = "fix.vehicle.telemetry"

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._fix_feed_m48()
        return records

    def _fix_feed_m48(self):
        Device = self.env["fix.iot.device"].sudo()
        for rec in self.sudo():
            devices = Device.search(
                [("vehicle_id", "=", rec.vehicle_id.id), ("decommissioned", "=", False)]
            )
            if rec.device_ref:
                named = devices.filtered(lambda d, ref=rec.device_ref: d.device_id == ref)
                devices = named or devices
            if not devices:
                continue
            values = {m: rec[f] for m, f in VEHICLE_METRICS.items()}
            _feed(_live_streams(self.env, devices), values, rec.last_ping, rec.name)


class FixMonitoredAssetM48(models.Model):
    _inherit = "fix.monitored.asset"

    @api.model
    def ingest_telemetry(self, agent_id, health, seen_at):
        result = super().ingest_telemetry(agent_id, health, seen_at)
        asset = self.sudo().search([("agent_id", "=", agent_id)], limit=1)
        devices = (
            self.env["fix.iot.device"]
            .sudo()
            .search([("monitored_asset_id", "=", asset.id), ("decommissioned", "=", False)])
            if asset
            else self.env["fix.iot.device"]
        )
        if devices:
            values = {m: asset[f] for m, f in ENDPOINT_METRICS.items()}
            values["endpoint_health"] = ENDPOINT_HEALTH.get(health)
            _feed(_live_streams(self.env, devices), values, seen_at, asset.agent_id)
        return result
