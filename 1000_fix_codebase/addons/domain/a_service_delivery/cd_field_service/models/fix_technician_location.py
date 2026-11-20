# fix.technician.location — Real-Time GPS Tracking with NFR-056 Throttle Guard (CD-M02-01)
import math

from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish  # FF-28


class FixTechnicianLocation(models.Model):
    """Latest GPS location telemetry ping with NFR-056 event-storm throttle protection."""

    _name = "fix.technician.location"
    _description = "Technician Location Ping"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "timestamp desc, id desc"

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
        string="Ping Reference",
        required=True,
        copy=False,
        readonly=True,
        default="/",
    )
    name_bn = fields.Char(
        string="Ping Reference (Bengali)",
        help="DE-17 Bengali-first presentation",
    )

    technician_id = fields.Many2one(
        "hr.employee",
        string="Technician",
        required=True,
        index=True,
    )
    latitude = fields.Float(
        string="Latitude",
        digits=(10, 7),
        required=True,
    )
    longitude = fields.Float(
        string="Longitude",
        digits=(10, 7),
        required=True,
    )
    speed_kmh = fields.Float(string="Speed (km/h)", default=0.0)
    accuracy_m = fields.Float(string="Accuracy (m)", default=5.0)
    battery_pct = fields.Integer(string="Battery %", default=100)
    timestamp = fields.Datetime(
        string="Ping Time",
        default=fields.Datetime.now,
        required=True,
        index=True,
    )
    zone_id = fields.Many2one("fix.zone", string="Current Zone")
    is_throttled = fields.Boolean(
        string="Throttled by NFR-056",
        default=False,
        help="Marked true if ping occurred within 30s rate limit window or < 100m distance threshold.",
    )
    # FLAW-02.2: Anti-Spoofing GNSS & Mock Location Telemetry
    is_mock_location = fields.Boolean(
        string="Mock Location Flagged",
        default=False,
        help="FLAW-02.2: True if OS mock-location provider or GPS spoofing heuristic detected.",
    )
    gnss_hdop = fields.Float(
        string="GNSS HDOP (Horizontal Dilution of Precision)",
        default=1.0,
        help="Horizontal dilution of precision (< 2.0 ideal, > 5.0 degraded/suspect).",
    )

    @api.model_create_multi
    def create(self, vals_list):
        # A02 ERP audit pass 2 M02-08: a technician records his OWN position,
        # stamped by the server; pings are never edited (no write ACL). A
        # dispatcher (or the superuser sync) may record for anyone.
        trusted = self.env.su or self.env.user.has_group(
            "cd_field_service.group_fix_field_service_manager"
        )
        own = (
            self.env["hr.employee"].sudo().search([("user_id", "=", self.env.uid)]).ids
            if not trusted
            else []
        )
        for vals in vals_list:
            if not trusted:
                if vals.get("technician_id") not in own:
                    raise UserError("A technician records only his own location.")
                vals["timestamp"] = fields.Datetime.now()
            if vals.get("name", "/") == "/":
                seq = self.env["ir.sequence"].next_by_code("fix.technician.location")
                vals["name"] = (
                    seq or f"LOC/{fields.Date.today().year}/{self.search_count([]) + 1:06d}"
                )
            if not vals.get("name_bn") and vals.get("name"):
                vals["name_bn"] = vals["name"]
        return super().create(vals_list)

    @api.model
    def record_ping(
        self,
        technician_id,
        lat,
        lon,
        speed=0.0,
        accuracy=5.0,
        battery=100,
        is_mock_location=False,
        gnss_hdop=1.0,
    ):
        """Record real-time location ping with NFR-056 rate-limiting (30s interval or 100m threshold)."""
        tech = self.env["hr.employee"].browse(technician_id)
        if not tech.exists():
            return False

        last_ping = self.search(
            [("technician_id", "=", technician_id)], order="timestamp desc", limit=1
        )
        now = fields.Datetime.now()
        is_throttled = False

        if last_ping:
            # Check elapsed seconds
            elapsed = (now - last_ping.timestamp).total_seconds()
            dist = self._calc_distance(lat, lon, last_ping.latitude, last_ping.longitude)
            # NFR-056 rule: throttle if elapsed < 30 seconds AND distance moved < 100m
            if elapsed < 30.0 and dist < 100.0:
                is_throttled = True

        comp_id = tech.company_id.id if tech.company_id else self.env.company.id
        ou_id = tech.operating_unit_id.id if tech.operating_unit_id else False
        if not ou_id:
            first_ou = self.env["operating.unit"].search([("company_id", "=", comp_id)], limit=1)
            ou_id = first_ou.id if first_ou else False

        ping = self.create(
            {
                "technician_id": technician_id,
                "company_id": comp_id,
                "operating_unit_id": ou_id,
                "latitude": lat,
                "longitude": lon,
                "speed_kmh": speed,
                "accuracy_m": accuracy,
                "battery_pct": battery,
                "timestamp": now,
                "is_throttled": is_throttled,
                "is_mock_location": bool(is_mock_location),
                "gnss_hdop": float(gnss_hdop or 1.0),
            }
        )

        # Only emit outbox event if not throttled (the old guard tested an EMPTY,
        # hence falsy, outbox recordset and called a non-existent create_event:
        # no ping event was ever emitted).
        if not is_throttled:
            publish(
                self.env,
                "technician.location.ping",
                "fix.technician.location",
                ping.id,
                {
                    "technician_id": technician_id,
                    "latitude": lat,
                    "longitude": lon,
                    "speed_kmh": speed,
                    "battery_pct": battery,
                    "timestamp": now.isoformat(),
                },
            )

        return ping

    @staticmethod
    def _calc_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Haversine distance in meters."""
        r = 6371000.0
        p1, p2 = math.radians(lat1), math.radians(lat2)
        dp = math.radians(lat2 - lat1)
        dl = math.radians(lon2 - lon1)
        a = math.sin(dp / 2.0) ** 2 + math.cos(p1) * math.cos(p2) * (math.sin(dl / 2.0) ** 2)
        return 2.0 * r * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
