# fix.field.order — Field Service Order & Execution Unit (CD-M02-01)
import json
import math
from datetime import datetime, timezone

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class FixFieldOrder(models.Model):
    """Field service order executing on-site customer repairs and diagnostics."""
    _name = "fix.field.order"
    _description = "Field Service Order"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "priority desc, scheduled_start asc, id desc"

    # Multi-tenant scoping per AS-03
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Operating Unit",
        required=True,
        index=True,
    )

    name = fields.Char(
        string="Order Reference",
        required=True,
        copy=False,
        readonly=True,
        default="/",
        tracking=True,
    )
    name_bn = fields.Char(
        string="Order Reference (Bengali)",
        help="DE-17 Bengali-first presentation",
        tracking=True,
    )

    order_id = fields.Many2one(
        "fix.service.order",
        string="Service Order",
        required=True,
        index=True,
        tracking=True,
    )
    technician_id = fields.Many2one(
        "hr.employee",
        string="Assigned Technician",
        tracking=True,
        index=True,
    )
    zone_id = fields.Many2one(
        "fix.zone",
        string="Dispatch Zone",
        required=True,
        index=True,
        tracking=True,
    )
    geofence_id = fields.Many2one(
        "fix.geofence",
        string="Geofence Boundary",
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pending_dispatch", "Pending Dispatch"),
            ("dispatched", "Dispatched"),
            ("accepted", "Accepted"),
            ("declined", "Declined"),
            ("en_route", "En Route"),
            ("arrived", "Arrived On Site"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )

    priority = fields.Selection(
        [
            ("0", "Low"),
            ("1", "Normal"),
            ("2", "High"),
            ("3", "Urgent"),
        ],
        string="Priority",
        default="1",
        tracking=True,
        index=True,
    )

    scheduled_start = fields.Datetime(
        string="Scheduled Start",
        tracking=True,
    )
    scheduled_end = fields.Datetime(
        string="Scheduled End",
        tracking=True,
    )
    sla_deadline = fields.Datetime(
        string="SLA Deadline",
        tracking=True,
    )

    customer_address = fields.Text(string="Customer Address")
    latitude = fields.Float(
        string="Latitude",
        digits=(10, 7),
    )
    longitude = fields.Float(
        string="Longitude",
        digits=(10, 7),
    )

    travel_time_est_minutes = fields.Float(
        string="Est. Travel Time (min)",
        default=0.0,
    )
    actual_travel_minutes = fields.Float(
        string="Actual Travel Time (min)",
        default=0.0,
    )
    distance_km = fields.Float(
        string="Estimated Distance (km)",
        default=0.0,
    )

    van_location_id = fields.Many2one(
        "fix.stock.location",
        string="Technician Van Location",
        domain="[('is_van_stock', '=', True)]",
    )

    decline_reason = fields.Selection(
        [
            ("capacity", "Capacity Exceeded / Overbooked"),
            ("distance", "Outside Commute Range"),
            ("skill_gap", "Missing Tool / Skill Requirement"),
            ("emergency", "Personal / Vehicle Emergency"),
            ("other", "Other Reason"),
        ],
        string="Decline Reason",
        tracking=True,
    )
    decline_notes = fields.Text(string="Decline Notes")
    notes = fields.Text(string="Special Instructions")
    active = fields.Boolean(default=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                seq = self.env["ir.sequence"].next_by_code("fix.field.order")
                vals["name"] = seq or f"FO/{fields.Date.today().year}/{self.search_count([]) + 1:05d}"
            if not vals.get("name_bn") and vals.get("name"):
                vals["name_bn"] = vals["name"]
        return super().create(vals_list)

    def action_request_dispatch(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only draft field orders can be submitted for dispatch.")
            rec.state = "pending_dispatch"

    def action_dispatch(self, technician_id=None):
        for rec in self:
            if rec.state not in ("draft", "pending_dispatch", "declined"):
                raise UserError(f"Cannot dispatch order in state '{rec.state}'.")
            if technician_id:
                rec.technician_id = technician_id
            if not rec.technician_id:
                raise UserError("A technician must be assigned to dispatch the field order.")
            
            # Check technician van stock location
            van = self.env["fix.stock.location"].search([
                ("technician_id", "=", rec.technician_id.id),
                ("is_van_stock", "=", True),
            ], limit=1)
            if van:
                rec.van_location_id = van.id

            rec.state = "dispatched"
            rec._emit_field_event("field.order.dispatched", {
                "field_order_id": rec.id,
                "order_ref": rec.name,
                "service_order_ref": rec.order_id.name if rec.order_id else "",
                "technician_id": rec.technician_id.id,
                "technician_name": rec.technician_id.name,
                "zone_id": rec.zone_id.id if rec.zone_id else False,
                "scheduled_start": rec.scheduled_start.isoformat() if rec.scheduled_start else None,
            })

    def action_accept(self):
        for rec in self:
            if rec.state != "dispatched":
                raise UserError("Only dispatched orders can be accepted.")
            rec.state = "accepted"
            rec._emit_field_event("field.order.accepted", {
                "field_order_id": rec.id,
                "order_ref": rec.name,
                "technician_id": rec.technician_id.id if rec.technician_id else False,
                "accepted_at": fields.Datetime.now().isoformat(),
            })

    def action_decline(self, reason="other", notes=""):
        DeclineLog = self.env["fix.field.decline.log"]
        for rec in self:
            if rec.state != "dispatched":
                raise UserError("Only dispatched orders can be declined.")
            prev_tech = rec.technician_id
            rec.write({
                "state": "declined",
                "decline_reason": reason,
                "decline_notes": notes,
                "technician_id": False,
            })
            DeclineLog.create({
                "field_order_id": rec.id,
                "technician_id": prev_tech.id if prev_tech else False,
                "company_id": rec.company_id.id,
                "operating_unit_id": rec.operating_unit_id.id,
                "reason": reason,
                "notes": notes,
            })
            rec._emit_field_event("field.order.declined", {
                "field_order_id": rec.id,
                "order_ref": rec.name,
                "declined_technician_id": prev_tech.id if prev_tech else False,
                "reason": reason,
                "notes": notes,
                "declined_at": fields.Datetime.now().isoformat(),
            })

    def action_start_travel(self):
        for rec in self:
            if rec.state != "accepted":
                raise UserError("Technician must accept the order before starting travel.")
            rec.state = "en_route"

    def action_arrive(self, current_lat=None, current_lon=None):
        for rec in self:
            if rec.state != "en_route":
                raise UserError("Order must be en route to mark arrival.")
            if current_lat is not None and current_lon is not None and rec.geofence_id:
                in_fence = rec._check_geofence_arrival(current_lat, current_lon)
                if not in_fence:
                    rec._emit_field_event("geofence.breach.detected", {
                        "field_order_id": rec.id,
                        "order_ref": rec.name,
                        "technician_id": rec.technician_id.id if rec.technician_id else False,
                        "current_lat": current_lat,
                        "current_lon": current_lon,
                        "geofence_id": rec.geofence_id.id,
                        "detail": "Arrival recorded outside designated geofence perimeter.",
                    })
            rec.state = "arrived"

    def action_start_work(self):
        for rec in self:
            if rec.state != "arrived":
                raise UserError("Technician must arrive on site before commencing work.")
            rec.state = "in_progress"

    def action_complete(self):
        for rec in self:
            if rec.state != "in_progress":
                raise UserError("Only in-progress orders can be completed.")
            rec.state = "completed"

    def action_cancel(self, reason=""):
        for rec in self:
            if rec.state == "completed":
                raise UserError("Completed orders cannot be cancelled.")
            rec.state = "cancelled"
            if reason:
                rec.notes = f"{rec.notes or ''}\nCancellation: {reason}".strip()

    def _check_geofence_arrival(self, lat: float, lon: float) -> bool:
        """Validate if current coordinates fall within the assigned geofence."""
        if not self.geofence_id or not self.geofence_id.geometry_json:
            return True
        try:
            geom = json.loads(self.geofence_id.geometry_json)
        except Exception:
            return True

        if self.geofence_id.geofence_type == "circle":
            center_lat = float(geom.get("lat", 0.0))
            center_lon = float(geom.get("lng", 0.0))
            radius_m = float(geom.get("radius_m", 500.0))
            # Haversine distance
            dist = self._haversine_distance(lat, lon, center_lat, center_lon)
            return dist <= radius_m
        else:
            # Polygon ray-casting algorithm
            points = geom.get("points", [])
            if len(points) < 3:
                return True
            inside = False
            j = len(points) - 1
            for i in range(len(points)):
                xi, yi = points[i][0], points[i][1]
                xj, yj = points[j][0], points[j][1]
                if ((yi > lon) != (yj > lon)) and (lat < (xj - xi) * (lon - yi) / (yj - yi) + xi):
                    inside = not inside
                j = i
            return inside

    @staticmethod
    def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Returns distance in meters between two lat/lon pairs."""
        r = 6371000.0  # Earth radius in meters
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlam = math.radians(lon2 - lon1)
        a = (math.sin(dphi / 2.0) ** 2 +
             math.cos(phi1) * math.cos(phi2) * (math.sin(dlam / 2.0) ** 2))
        return 2.0 * r * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    def _emit_field_event(self, event_type: str, payload: dict):
        """Emit domain event through cd_event_outbox per AS-08."""
        Outbox = self.env.get("fix.event.outbox")
        if Outbox:
            Outbox.create_event(
                event_type=event_type,
                aggregate_type="fix.field.order",
                aggregate_id=str(self.id),
                payload=payload,
            )
