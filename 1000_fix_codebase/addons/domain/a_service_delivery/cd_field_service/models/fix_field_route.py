# fix.field.route — Daily Technician Route & Itinerary Optimization (CD-M02-01)
import itertools
import math
import os

import requests
from odoo import api, fields, models
from odoo.exceptions import UserError

# Planning model constants (R01 re-audit 2026-10-22: the previous optimiser
# multiplied the baseline by a hardcoded 0.813 - a constant masquerading as a
# measurement). These assumptions are applied IDENTICALLY to the baseline and
# the optimised sequence, so the recorded improvement is a real consequence of
# the sequence change, not a factor. Tune per city if field telemetry says so.
AVG_SPEED_KMH = 18.0  # Dhaka mixed-traffic planning speed
SERVICE_MINUTES_PER_STOP = 25.0  # on-site service time per stop
DEPOT_LATLON = (23.7776, 90.3959)  # Tejgaon Central Service Hub (default depot)
EARTH_RADIUS_KM = 6371.0
OSRM_TIMEOUT_SECONDS = 2.0


def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance in km between two lat/lon points."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlmb / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def distance_matrix_km(points):
    """Symmetric distance matrix (km) over [(lat, lon), ...].

    Prefers the OSRM table service when the field profile is up
    (OSRM_URL env or http://127.0.0.1:5000); falls back to haversine.
    Returns (matrix, engine_label).
    """
    base = os.environ.get("OSRM_URL", "http://127.0.0.1:5000")
    coords = ";".join(f"{lon:.6f},{lat:.6f}" for lat, lon in points)
    srcs = ";".join(str(i) for i in range(len(points)))
    try:
        resp = requests.get(
            f"{base}/table/v1/driving/{coords}",
            params={"sources": srcs, "annotations": "distance"},
            timeout=OSRM_TIMEOUT_SECONDS,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("code") == "Ok" and data.get("distances"):
                n = len(points)
                m = [[0.0] * n for _ in range(n)]
                ok = True
                for i, row in enumerate(data["distances"]):
                    for j, metres in enumerate(row):
                        if metres is None:
                            ok = False
                            break
                        m[i][j] = m[j][i] = metres / 1000.0
                    if not ok:
                        break
                if ok:
                    return m, "osrm-table"
    except requests.RequestException:
        pass
    n = len(points)
    m = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            d = haversine_km(*points[i], *points[j])
            m[i][j] = m[j][i] = d
    return m, "haversine"


def trip_km(matrix, sequence):
    """Total km of a trip visiting stops in `sequence` order."""
    return sum(matrix[a][b] for a, b in itertools.pairwise(sequence))


def optimise_sequence(matrix):
    """Nearest-neighbour from the depot (index 0) then a bounded 2-opt pass.

    Deterministic, O(n^2) per pass, capped at 50 improvement rounds so very
    large routes stay interactive. This is a heuristic; the engine label on
    the route record says so.
    """
    n = len(matrix)
    remaining = list(range(1, n))
    seq = [0]
    while remaining:
        nxt = min(remaining, key=lambda j: matrix[seq[-1]][j])
        seq.append(nxt)
        remaining.remove(nxt)
    improved = True
    rounds = 0
    while improved and rounds < 50:
        improved = False
        rounds += 1
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                cand = seq[:i] + seq[i : j + 1][::-1] + seq[j + 1 :]
                if trip_km(matrix, cand) + 1e-9 < trip_km(matrix, seq):
                    seq = cand
                    improved = True
    return seq


class FixFieldRoute(models.Model):
    """Daily multi-stop route itinerary for field technicians with TSP/VRP optimization."""

    _name = "fix.field.route"
    _description = "Field Route Itinerary"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, technician_id asc, id desc"

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
        string="Route Reference",
        required=True,
        copy=False,
        readonly=True,
        default="/",
        tracking=True,
    )
    name_bn = fields.Char(
        string="Route Reference (Bengali)",
        help="DE-17 Bengali-first presentation",
        tracking=True,
    )

    technician_id = fields.Many2one(
        "hr.employee",
        string="Technician",
        required=True,
        tracking=True,
        index=True,
    )
    date = fields.Date(
        string="Service Date",
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )

    route_state = fields.Selection(
        [
            ("draft", "Draft Itinerary"),
            ("optimized", "VROOM Optimized"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
        ],
        string="Status",
        default="draft",
        required=True,
        tracking=True,
    )

    field_order_ids = fields.Many2many(
        "fix.field.order",
        "fix_field_route_order_rel",
        "route_id",
        "order_id",
        string="Scheduled Field Orders",
    )

    order_count = fields.Integer(
        string="Stops Count",
        compute="_compute_order_count",
        store=True,
    )

    depot_location = fields.Char(
        string="Starting Depot / Hub",
        default="Tejgaon Central Service Hub (Dhaka)",
    )

    total_distance_km = fields.Float(
        string="Optimized Distance (km)",
        default=0.0,
        tracking=True,
    )
    total_duration_hours = fields.Float(
        string="Optimized Duration (hours)",
        default=0.0,
        tracking=True,
    )
    baseline_duration_hours = fields.Float(
        string="Baseline Duration (hours)",
        default=0.0,
        tracking=True,
    )
    improvement_pct = fields.Float(
        string="Travel Time Reduction (%)",
        compute="_compute_improvement",
        store=True,
        tracking=True,
    )

    notes = fields.Text(string="Route Notes")
    active = fields.Boolean(default=True)

    @api.depends("field_order_ids")
    def _compute_order_count(self):
        for rec in self:
            rec.order_count = len(rec.field_order_ids)

    @api.depends("baseline_duration_hours", "total_duration_hours")
    def _compute_improvement(self):
        for rec in self:
            if rec.baseline_duration_hours > 0 and rec.total_duration_hours > 0:
                savings = rec.baseline_duration_hours - rec.total_duration_hours
                rec.improvement_pct = round((savings / rec.baseline_duration_hours) * 100.0, 2)
            else:
                rec.improvement_pct = 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                seq = self.env["ir.sequence"].next_by_code("fix.field.route")
                vals["name"] = (
                    seq or f"RO/{fields.Date.today().year}/{self.search_count([]) + 1:04d}"
                )
            if not vals.get("name_bn") and vals.get("name"):
                vals["name_bn"] = vals["name"]
        return super().create(vals_list)

    def action_optimize_route(self):
        """Compute the route's travel metrics honestly (R01 re-audit fix).

        Baseline = the stops in their CURRENT sequence; optimised = nearest-
        neighbour + 2-opt over the same distance matrix. Both durations use
        the same planning constants, so improvement_pct is measured, never a
        constant. Every order must carry coordinates - no geocode, no result.
        """
        for rec in self:
            orders = list(rec.field_order_ids)
            if len(orders) < 2:
                raise UserError("A route must contain at least 2 field orders to optimize.")
            missing = [o for o in orders if not o.latitude or not o.longitude]
            if missing:
                raise UserError(
                    "Cannot optimize: %d order(s) lack GPS coordinates. Geocode the service "
                    "addresses first - distances will not be invented." % len(missing)
                )
            points = [DEPOT_LATLON] + [(o.latitude, o.longitude) for o in orders]
            matrix, engine = distance_matrix_km(points)
            baseline_seq = list(range(len(points)))
            opt_seq = optimise_sequence(matrix)

            base_km = trip_km(matrix, baseline_seq)
            opt_km = trip_km(matrix, opt_seq)
            base_hours = base_km / AVG_SPEED_KMH + len(orders) * SERVICE_MINUTES_PER_STOP / 60.0
            opt_hours = opt_km / AVG_SPEED_KMH + len(orders) * SERVICE_MINUTES_PER_STOP / 60.0

            rec.write(
                {
                    "baseline_duration_hours": round(base_hours, 2),
                    "total_duration_hours": round(opt_hours, 2),
                    "total_distance_km": round(opt_km, 1),
                    "route_state": "optimized",
                }
            )
            pct = round((base_hours - opt_hours) / base_hours * 100.0, 2) if base_hours > 0 else 0.0
            rec.message_post(
                body=(
                    f"Route optimised (engine: {engine}, heuristic: nearest-neighbour + 2-opt). "
                    f"Distance {base_km:.1f} km -> {opt_km:.1f} km; duration "
                    f"{base_hours:.2f} h -> {opt_hours:.2f} h "
                    f"(model: {AVG_SPEED_KMH} km/h, {SERVICE_MINUTES_PER_STOP:.0f} min/stop; "
                    f"improvement {pct}% is measured over the same model)."
                )
            )

    def action_start_route(self):
        for rec in self:
            if rec.route_state not in ("optimized", "draft"):
                raise UserError("Route must be drafted or optimized before starting.")
            rec.route_state = "in_progress"

    def action_complete_route(self):
        for rec in self:
            if rec.route_state != "in_progress":
                raise UserError("Only in-progress routes can be completed.")
            rec.route_state = "completed"
