# A02 ERP audit pass 2 M03-05 (owner decision D22): pick-and-drop charges.
#
# The consignment computed freight figures (base freight, volumetric surcharge,
# insurance) from courier rates or hard-coded 80 / 40 BDT, and nothing ever
# charged the customer for a pickup or a delivery. The charge is now a record:
# a zone x weight tariff (default EMPTY = no charge, D22), applied when a leg
# of a service order is confirmed, waived for warranty and AMC orders, kept on
# the leg and announced (logistics.charge_calculated) so the order's billing
# picks it up. fix.service.order._fix_logistics_charges() is the order-side
# total.
from odoo import api, fields, models
from odoo.exceptions import ValidationError

from libs.py.fix_events import publish  # FF-28

WAIVED_CATEGORIES = ("warranty", "amc")


class FixLogisticsTariff(models.Model):
    _name = "fix.logistics.tariff"
    _description = "Pick & Drop Tariff (zone x weight)"
    _order = "zone_id, consignment_type, weight_from_kg, id"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    zone_id = fields.Many2one(
        "fix.zone", string="Zone", index=True, help="Empty = every zone without its own row."
    )
    consignment_type = fields.Selection(
        [("pickup", "Pickup"), ("delivery", "Delivery"), ("any", "Pickup or Delivery")],
        string="Leg",
        required=True,
        default="any",
    )
    weight_from_kg = fields.Float(string="From (kg)", required=True, default=0.0)
    weight_to_kg = fields.Float(string="Up To (kg)", required=True, default=0.0)
    charge_bdt = fields.Float(string="Charge (BDT, excl. VAT)", required=True, default=0.0)
    active = fields.Boolean(default=True)

    @api.constrains("weight_from_kg", "weight_to_kg", "charge_bdt")
    def _check_band(self):
        for rec in self:
            if rec.weight_from_kg < 0 or rec.weight_to_kg <= rec.weight_from_kg:
                raise ValidationError("A tariff band runs from a weight up to a larger one.")
            if rec.charge_bdt < 0:
                raise ValidationError("A tariff charge cannot be negative.")

    @api.model
    def _fix_rate(self, company, zone, consignment_type, weight_kg):
        """The band that prices this leg: the zone's own row first, then the
        any-zone row; the leg type's own row before the 'any' row."""
        Tariff = self.sudo()
        zone_domains = [[("zone_id", "=", zone.id)]] if zone else []
        zone_domains.append([("zone_id", "=", False)])
        for zone_dom in zone_domains:
            for ctype in (consignment_type, "any"):
                band = Tariff.search(
                    [
                        ("company_id", "=", company.id),
                        ("consignment_type", "=", ctype),
                        ("weight_from_kg", "<=", weight_kg),
                        ("weight_to_kg", ">", weight_kg),
                        *zone_dom,
                    ],
                    limit=1,
                )
                if band:
                    return band
        return Tariff.browse()


class FixConsignmentCharge(models.Model):
    _inherit = "fix.consignment"

    zone_id = fields.Many2one(
        "fix.zone",
        string="Customer Zone",
        help="The zone the customer's address is in; it prices the pick & drop charge.",
    )
    logistics_tariff_id = fields.Many2one(
        "fix.logistics.tariff", string="Tariff Band", readonly=True, copy=False
    )
    logistics_charge_bdt = fields.Float(
        string="Pick & Drop Charge (BDT)", readonly=True, copy=False
    )
    logistics_charge_note = fields.Char(string="Charge Basis", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "logistics_tariff_id",
            "logistics_charge_bdt",
            "logistics_charge_note",
        }

    def _m03_price_leg(self):
        """D22: the tariff charge of this leg, or a recorded waiver."""
        self.ensure_one()
        if not self.service_order_id or self.consignment_type not in ("pickup", "delivery"):
            return
        order = self.service_order_id.sudo()
        zone = self.zone_id or order.branch_id.zone_id
        weight = (
            self.chargeable_weight_kg
            or self.actual_weight_kg
            or ((self.dispatch_weight_g or 0.0) / 1000.0)
        )
        band = self.env["fix.logistics.tariff"]._fix_rate(
            self.company_id, zone, self.consignment_type, weight
        )
        if not band:
            vals = {
                "logistics_tariff_id": False,
                "logistics_charge_bdt": 0.0,
                "logistics_charge_note": "no tariff band (no charge)",
            }
        elif order.order_category in WAIVED_CATEGORIES:
            vals = {
                "logistics_tariff_id": band.id,
                "logistics_charge_bdt": 0.0,
                "logistics_charge_note": "waived: %s order (tariff BDT %.2f)"
                % (order.order_category, band.charge_bdt),
            }
        else:
            vals = {
                "logistics_tariff_id": band.id,
                "logistics_charge_bdt": band.charge_bdt,
                "logistics_charge_note": "%s, %.3f kg: BDT %.2f"
                % (zone.name or "any zone", weight, band.charge_bdt),
            }
        self._guarded().write(vals)
        publish(
            self.env,
            "logistics.charge_calculated",
            "fix.consignment",
            self.id,
            {
                "consignment": self.name,
                "consignment_type": self.consignment_type,
                "service_order_id": order.id,
                "amount_bdt": vals["logistics_charge_bdt"],
                "tariff_id": vals["logistics_tariff_id"],
                "basis": vals["logistics_charge_note"],
            },
        )

    def action_confirm(self):
        # priced BEFORE the confirm derives a delivery leg's cash on delivery,
        # so the COD the rider collects includes this leg's own charge (it was
        # priced after, and the leg then never matched the amount due)
        for rec in self.filtered(lambda c: c.state == "draft"):
            rec._m03_price_leg()
        return super().action_confirm()


class FixServiceOrderLogisticsCharge(models.Model):
    _inherit = "fix.service.order"

    def _fix_charged_legs(self):
        """The legs whose pick & drop charge the customer pays: priced, and
        not returned or lost (a draft leg is priced only while it confirms)."""
        self.ensure_one()
        return self.sudo().consignment_ids.filtered(
            lambda c: c.state not in ("returned", "lost") and c.logistics_charge_bdt > 0.005
        )

    def _fix_logistics_charges(self) -> float:
        """The pick & drop charges (excl. VAT) of this order (M03-05, D22)."""
        return round(sum(self._fix_charged_legs().mapped("logistics_charge_bdt")), 2)

    def _fix_extra_charges(self) -> list:
        """D22: each charged leg is billed with the repair (CHG-TRANSPORT)."""
        charges = super()._fix_extra_charges()
        for leg in self._fix_charged_legs().sorted("id"):
            charges.append(
                {
                    "code": "CHG-TRANSPORT",
                    "line_type": "transport",
                    "description": "%s charge %s (%s)"
                    % (
                        "Pick-up" if leg.consignment_type == "pickup" else "Delivery",
                        leg.name,
                        leg.logistics_charge_note or "tariff",
                    ),
                    "net": round(leg.logistics_charge_bdt, 2),
                }
            )
        return charges

    def action_create_consignment(self):
        legs = super().action_create_consignment()
        for leg in legs:
            zone = leg.service_order_id.sudo().branch_id.zone_id
            if zone and not leg.zone_id:
                leg.sudo().write({"zone_id": zone.id})
        return legs
