# fix.field.route — Daily Technician Route & Itinerary Optimization (CD-M02-01)
import itertools
import json
import math
import os

import requests
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

# Planning model constants (R01 re-audit 2026-10-22: the previous optimiser
# multiplied the baseline by a hardcoded 0.813 - a constant masquerading as a
# measurement). These assumptions are applied IDENTICALLY to the baseline and
# the optimised sequence, so the recorded improvement is a real consequence of
# the sequence change, not a factor. Tune per city if field telemetry says so.
AVG_SPEED_KMH = 18.0  # Dhaka mixed-traffic planning speed
SERVICE_MINUTES_PER_STOP = 25.0  # on-site service time per stop
# A02 ERP audit M02-F11: the depot was hard-coded to Tejgaon (23.7776, 90.3959)
# whatever the route said. The route now starts from its OWN depot position;
# none means no optimisation (distances are not invented from a guessed hub).
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
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "date desc, technician_id asc, id desc"

    # A02 audit M02-1: route_state (and the optimiser's measured result) moved
    # only through the route actions; a plain write set any of them.
    _GUARDED_FIELDS = frozenset(
        {
            "route_state",
            "total_distance_km",
            "total_duration_hours",
            "baseline_duration_hours",
            # A02 ERP audit M02-F11: the optimised visiting order
            "stop_sequence_json",
            "stop_plan",
        }
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self._GUARDED_FIELDS

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
        default=lambda self: self.env.user.default_operating_unit_id
        or self.env["operating.unit"].sudo().search([], limit=1),
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
        help="The depot's name. Its position is the Depot Latitude / Longitude; a name "
        "alone cannot be measured from.",
    )
    depot_latitude = fields.Float(string="Depot Latitude", digits=(10, 7))
    depot_longitude = fields.Float(string="Depot Longitude", digits=(10, 7))
    stop_sequence_json = fields.Text(
        string="Optimised Stop Order (JSON)",
        readonly=True,
        copy=False,
        help="The field order ids in the order the optimiser visits them.",
    )
    stop_plan = fields.Text(string="Optimised Stop Order", readonly=True, copy=False)

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

    @api.constrains("technician_id", "field_order_ids")
    def _check_stops_belong_to_the_technician(self):
        """A route is one technician's day: no stop is another technician's
        field order, and none is cancelled (bidirectional audit 2026-11-13;
        the stops became editable on the workspace Route Plan). An order not
        yet dispatched may be planned onto the route before it is sent."""
        for route in self:
            tech = route.technician_id
            foreign = route.field_order_ids.filtered(
                lambda o, tech=tech: o.technician_id and o.technician_id != tech
            )
            if foreign:
                raise ValidationError(
                    "Route %s is %s's day: %s %s dispatched to someone else."
                    % (
                        route.name,
                        route.technician_id.name,
                        ", ".join(foreign.mapped("name")),
                        "is" if len(foreign) == 1 else "are",
                    )
                )
            cancelled = route.field_order_ids.filtered(lambda o: o.state == "cancelled")
            if cancelled:
                raise ValidationError(
                    "A cancelled field order is not a stop: %s."
                    % ", ".join(cancelled.mapped("name"))
                )

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
            # operating_unit_id is required with no default — resolve it like
            # the field order does, else EVERY route created from a UI/API
            # (including the D365 Route Plan form) dies with NotNullViolation
            # (forensic audit D-M02-3).
            if not vals.get("operating_unit_id"):
                ou = (
                    self.env.user.default_operating_unit_id
                    or self.env["operating.unit"]
                    .sudo()
                    .search(
                        [("company_id", "=", vals.get("company_id", self.env.company.id))], limit=1
                    )
                    or self.env["operating.unit"].sudo().search([], limit=1)
                )
                if ou:
                    vals["operating_unit_id"] = ou.id
            if vals.get("name", "/") == "/":
                seq = self.env["ir.sequence"].next_by_code("fix.field.route")
                vals["name"] = (
                    seq or f"RO/{fields.Date.today().year}/{self.search_count([]) + 1:04d}"
                )
            if not vals.get("name_bn") and vals.get("name"):
                vals["name_bn"] = vals["name"]
        return super().create(vals_list)

    def write(self, vals):
        # A02 ERP audit M02-F11: an optimised plan is for the stops and depot it
        # was computed on. Changing either sends the route back to Draft with
        # no plan, instead of showing a sequence that no longer fits.
        replan = {"field_order_ids", "depot_latitude", "depot_longitude"} & set(vals)
        stale = self.browse()
        if replan:
            stale = self.filtered(lambda r: r.route_state == "optimized" or r.stop_plan)
            before = {
                r.id: (set(r.field_order_ids.ids), r.depot_latitude, r.depot_longitude)
                for r in stale
            }
        res = super().write(vals)
        if replan:
            changed = stale.filtered(
                lambda r: before[r.id]
                != (set(r.field_order_ids.ids), r.depot_latitude, r.depot_longitude)
            )
            for rec in changed:
                vals_reset = {"stop_sequence_json": False, "stop_plan": False}
                if rec.route_state == "optimized":
                    vals_reset["route_state"] = "draft"
                rec._guarded().write(vals_reset)
        return res

    def _fix_depot_point(self):
        """The route's own depot position, or a refusal."""
        self.ensure_one()
        lat, lon = self.depot_latitude, self.depot_longitude
        if not lat or not lon or abs(lat) > 90 or abs(lon) > 180:
            raise UserError(
                "Route %s has no depot position: give the Depot Latitude and Longitude of "
                "where the technician starts (%s). Distances are not measured from a guessed hub."
                % (self.name, self.depot_location or "no depot named")
            )
        return (lat, lon)

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
            points = [rec._fix_depot_point()] + [(o.latitude, o.longitude) for o in orders]
            matrix, engine = distance_matrix_km(points)
            baseline_seq = list(range(len(points)))
            opt_seq = optimise_sequence(matrix)

            base_km = trip_km(matrix, baseline_seq)
            opt_km = trip_km(matrix, opt_seq)
            base_hours = base_km / AVG_SPEED_KMH + len(orders) * SERVICE_MINUTES_PER_STOP / 60.0
            opt_hours = opt_km / AVG_SPEED_KMH + len(orders) * SERVICE_MINUTES_PER_STOP / 60.0

            # A02 ERP audit M02-F11: the optimised order was computed and thrown
            # away; it is now kept on the route (index 0 is the depot).
            visit = [orders[i - 1] for i in opt_seq if i]
            plan = [
                "%d. %s (%.1f km from %s)"
                % (
                    n,
                    order.name,
                    matrix[prev][cur],
                    "the depot" if prev == 0 else orders[prev - 1].name,
                )
                for n, (prev, cur) in enumerate(itertools.pairwise(opt_seq), start=1)
                for order in [orders[cur - 1]]
            ]
            rec._guarded().write(
                {
                    "baseline_duration_hours": round(base_hours, 2),
                    "total_duration_hours": round(opt_hours, 2),
                    "total_distance_km": round(opt_km, 1),
                    "route_state": "optimized",
                    "stop_sequence_json": json.dumps([o.id for o in visit]),
                    "stop_plan": "\n".join(plan),
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
            rec._guarded().write({"route_state": "in_progress"})

    def action_complete_route(self):
        for rec in self:
            if rec.route_state != "in_progress":
                raise UserError("Only in-progress routes can be completed.")
            rec._guarded().write({"route_state": "completed"})
