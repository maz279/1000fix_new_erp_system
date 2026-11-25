# fix_m48_asset_binding — A07 ERP audit (2026-11-20) M48-05 / M48-04.
#
# An M48 stream and a prediction bound only to M45 equipment or an M47 site, so a
# customer's device (M17), a vehicle (M46) or an MSP endpoint (M05) could not be
# monitored as itself, and a customer-premises prediction always waited for a
# person to "choose the device". The device now names one of them directly; a
# prediction names its equipment, vehicle or customer device (exactly one).
#
# Who pays (M48-04, BRU-IOT-13, AUT-IOT-14/15): work on a customer's device is
# raised only when an M08 contract in force covers the device AND the customer
# agreed to proactive service (a verified, valid M48 consent with Proactive
# Service ticked). Otherwise no order is raised: an M07 opportunity is published
# and the demand waits for a person (who may route it once the customer accepts).
from odoo import api, fields, models
from odoo.exceptions import ValidationError

from .fix_maintenance_demand import _today

CONTRACT_IN_FORCE = ("active", "expiring")


class FixIotDeviceAssets(models.Model):
    _inherit = "fix.iot.device"

    customer_device_id = fields.Many2one(
        "fix.device",
        string="Customer Device (M17)",
        ondelete="restrict",
        index=True,
        help="The customer's registered device this sensor or agent monitors.",
    )
    vehicle_id = fields.Many2one(
        "fleet.vehicle",
        string="Vehicle (M46)",
        ondelete="restrict",
        index=True,
        help="The fleet vehicle this tracker or telematics unit is fitted to.",
    )
    monitored_asset_id = fields.Many2one(
        "fix.monitored.asset",
        string="MSP Endpoint (M05)",
        ondelete="restrict",
        index=True,
        help="The M05 managed endpoint whose RMM readings this device's streams carry.",
    )

    def _fix_binding_fields(self) -> set:
        return super()._fix_binding_fields() | {
            "customer_device_id",
            "vehicle_id",
            "monitored_asset_id",
        }

    def _fix_company_asset(self):
        return super()._fix_company_asset() or self.vehicle_id

    def _fix_bound_asset(self):
        return (
            super()._fix_bound_asset()
            or self.customer_device_id
            or self.monitored_asset_id
            or self.vehicle_id
        )

    def _fix_customer_binding(self):
        reason = super()._fix_customer_binding()
        if reason:
            return reason
        if self.customer_device_id:
            return "the device monitors customer device %s" % self.customer_device_id.display_name
        if self.monitored_asset_id:
            return "the device carries MSP endpoint %s of a customer" % (
                self.monitored_asset_id.hostname or self.monitored_asset_id.agent_id
            )
        return ""

    def _fix_owner_module(self):
        if self.vehicle_id:
            return "M46"
        if self.monitored_asset_id:
            return "M05"
        if self.customer_device_id:
            return "M17"
        return super()._fix_owner_module()

    @api.constrains("customer_device_id", "monitored_asset_id")
    def _check_endpoint_device(self):
        for rec in self:
            asset = rec.monitored_asset_id.sudo()
            if (
                asset.device_id
                and rec.customer_device_id
                and asset.device_id != rec.customer_device_id
            ):
                raise ValidationError(
                    "MSP endpoint %s is registered device %s, not %s."
                    % (
                        asset.hostname or asset.agent_id,
                        asset.device_id.display_name,
                        rec.customer_device_id.display_name,
                    )
                )

    def _fix_customer_device(self):
        """The M17 device the work is done on (directly, or the endpoint's)."""
        self.ensure_one()
        return self.customer_device_id or self.monitored_asset_id.sudo().device_id


class FixPredictionAssets(models.Model):
    _inherit = "fix.predictive.maintenance"

    vehicle_id = fields.Many2one(
        "fleet.vehicle", string="Vehicle (M46)", ondelete="cascade", index=True
    )
    customer_device_id = fields.Many2one(
        "fix.device", string="Customer Device (M17)", ondelete="cascade", index=True
    )

    def _fix_prediction_asset(self):
        return super()._fix_prediction_asset() or self.vehicle_id or self.customer_device_id

    @api.constrains("equipment_id", "vehicle_id", "customer_device_id")
    def _check_one_asset(self):
        for rec in self:
            named = [f for f in ("equipment_id", "vehicle_id", "customer_device_id") if rec[f]]
            if len(named) != 1:
                raise ValidationError(
                    "Prediction %s names exactly one asset: the equipment, the vehicle or the "
                    "customer device it was computed for." % rec.name
                )


class FixIotActionCommercialRoute(models.Model):
    _inherit = "fix.iot.action"

    def _fix_commercial_route(self):
        """intervention.proposed tells M01/M07 who pays (spec §12.3)."""
        self.ensure_one()
        device = self.env["fix.maintenance.demand"]._spine_m48_customer_device(
            self.prediction_id.sudo()
        )
        if not device:
            return super()._fix_commercial_route()
        state, _contract, _why = self.env["fix.maintenance.demand"]._spine_entitlement(device)
        return {
            "entitlement_state": state,
            "commercial_route": "contract" if state == "entitled" else "opportunity",
        }


class FixIotHealthFaults(models.Model):
    _inherit = "fix.iot.health"

    @api.model
    def _fix_fault_history(self, device, since):
        """M48-13: repair work raised on the device's asset since `since`."""
        domain = [("work_type", "=", "repair"), ("create_date", ">=", since)]
        if device.equipment_id:
            domain.append(("equipment_id", "=", device.equipment_id.id))
        elif device.vehicle_id:
            domain.append(("vehicle_id", "=", device.vehicle_id.id))
        elif device._fix_customer_device():
            domain.append(("device_id", "=", device._fix_customer_device().id))
        else:
            return super()._fix_fault_history(device, since)
        return self.env["fix.maintenance.demand"].sudo().search_count(domain)


class FixMaintenanceDemandEntitlement(models.Model):
    _inherit = "fix.maintenance.demand"

    @api.model
    def _spine_proactive_consent(self, device):
        """A verified, valid M48 consent of the device's owner with Proactive
        Service agreed."""
        owner = device.owner_id.commercial_partner_id or device.owner_id
        if not owner:
            return self.env["fix.iot.consent"]
        today = _today(self.env)
        return (
            self.env["fix.iot.consent"]
            .sudo()
            .search([("partner_id", "child_of", owner.id), ("proactive_service", "=", True)])
            .filtered(lambda c: c._fix_is_valid(today))
        )

    @api.model
    def _spine_entitlement(self, device):
        """(state, contract, why) for work on the customer's M17 `device`:
        state is entitled / no_contract / no_consent."""
        Contract = self.env.get("fix.contract")
        today = _today(self.env)
        contract = self.env["fix.contract"].browse() if Contract is not None else None
        if Contract is not None:
            owner = device.owner_id.commercial_partner_id or device.owner_id
            for candidate in Contract.sudo().search(
                [
                    ("customer_id", "child_of", owner.id if owner else 0),
                    ("state", "in", CONTRACT_IN_FORCE),
                ]
            ):
                if candidate._contract_covers_device(device, today):
                    contract = candidate
                    break
        if not contract:
            return (
                "no_contract",
                contract,
                "no M08 contract in force covers device %s" % device.display_name,
            )
        if not self._spine_proactive_consent(device):
            return (
                "no_consent",
                contract,
                "the customer has not agreed to proactive service (no verified M48 consent "
                "with Proactive Service ticked)",
            )
        return "entitled", contract, ""
