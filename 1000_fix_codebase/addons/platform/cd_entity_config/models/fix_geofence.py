# fix.geofence — geographic fence for zone dispatch and attendance (P03-M04-T03).
# Coordinates are stored as a GeoJSON-ish JSON column; PostGIS lands in Phase 5
# (D-029 companion) — the shape and validation rules are stable from W1 so the
# dispatch module never rewrites them.
import json

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_REQUIRED_GEOFENCE_TYPES = ("circle", "polygon")


class FixGeofence(models.Model):
    """A geofence attached to a dispatch zone."""
    _name = "fix.geofence"
    _description = "Geofence"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Geofence Name", required=True, tracking=True)
    geofence_type = fields.Selection(
        [("circle", "Circle (centre + radius)"), ("polygon", "Polygon")],
        string="Type", required=True, default="circle")
    zone_id = fields.Many2one("fix.zone", string="Zone", required=True,
                              ondelete="cascade")
    # circle: {"lat": 23.79, "lng": 90.41, "radius_m": 500}
    # polygon: {"points": [[lat, lng], ...]} (min 3)
    geometry_json = fields.Text(string="Geometry (JSON)", required=True)
    active = fields.Boolean(default=True, tracking=True)

    @api.constrains("geofence_type", "geometry_json")
    def _check_geometry(self):
        for fence in self:
            try:
                geometry = json.loads(fence.geometry_json)
            except (TypeError, ValueError) as exc:
                raise ValidationError("Geofence geometry must be valid JSON") from exc
            if fence.geofence_type == "circle":
                for key in ("lat", "lng", "radius_m"):
                    if key not in geometry:
                        raise ValidationError(f"Circle geofence needs {key}")
                if not 0 < float(geometry["radius_m"]) <= 100_000:
                    raise ValidationError("radius_m must be within (0, 100000]")
            else:
                points = geometry.get("points", [])
                if len(points) < 3:
                    raise ValidationError("Polygon geofence needs at least 3 points")
                for lat, lng in points:
                    if not (-90 <= float(lat) <= 90 and -180 <= float(lng) <= 180):
                        raise ValidationError("Polygon point out of lat/lng range")
