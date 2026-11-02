# fix.field.order — Field Service Order & Execution Unit (CD-M02-01)
import json
import logging
import math

from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish  # FF-28

_logger = logging.getLogger(__name__)


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
        default=lambda self: self.env.user.default_operating_unit_id
        or self.env["operating.unit"].sudo().search([], limit=1),
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

    # Journey stamps (M02): written by the state actions so travel time and
    # on-time arrival are MEASURED, not estimated-only. actual_travel_minutes
    # existed as a field no code ever wrote.
    dispatched_at = fields.Datetime(string="Dispatched At", readonly=True, copy=False)
    accepted_at = fields.Datetime(string="Accepted At", readonly=True, copy=False)
    en_route_at = fields.Datetime(string="En Route At", readonly=True, copy=False)
    arrived_at = fields.Datetime(string="Arrived At", readonly=True, copy=False)
    started_work_at = fields.Datetime(string="Work Started At", readonly=True, copy=False)
    completed_at = fields.Datetime(string="Completed At", readonly=True, copy=False)
    on_time_arrival = fields.Boolean(
        string="Arrived On Time",
        compute="_compute_on_time_arrival",
        store=True,
        help="True when arrival was recorded at or before the scheduled start.",
    )

    @api.depends("arrived_at", "scheduled_start")
    def _compute_on_time_arrival(self):
        for rec in self:
            rec.on_time_arrival = bool(
                rec.arrived_at and rec.scheduled_start and rec.arrived_at <= rec.scheduled_start
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

    # --- A02 Enterprise Data Capture, GNSS Anti-Spoofing & On-Site Payment (FLAW-02.1..02.3, HS-08) ---
    district_name = fields.Char(string="Bangladesh District (64-District Geo)", tracking=True)
    thana_name = fields.Char(string="Thana / Upazila", tracking=True)
    is_mock_location = fields.Boolean(
        string="Mock Location Detected",
        default=False,
        tracking=True,
        help="FLAW-02.2: Hard-blocks on-site arrival check-in when OS mock location is active.",
    )
    gnss_hdop = fields.Float(
        string="GNSS HDOP",
        default=1.0,
        help="Horizontal dilution of precision at arrival check-in.",
    )
    oem_certification_verified = fields.Boolean(
        string="OEM Skill & Certification Verified",
        default=True,
        tracking=True,
    )
    safety_ppe_verified = fields.Boolean(
        string="HSE / Electrical PPE Checklist Verified",
        default=True,
        tracking=True,
    )
    lone_worker_checkin_at = fields.Datetime(
        string="Lone-Worker Safety Heartbeat",
        tracking=True,
    )
    diagnostic_tool_serial = fields.Char(
        string="Assigned Diagnostic Kit / Multimeter Serial",
    )
    work_summary = fields.Text(
        string="On-Site Engineering Execution Summary",
    )
    before_repair_photo_ref = fields.Char(
        string="Pre-Repair Site Photo Evidence Ref",
    )
    after_repair_photo_ref = fields.Char(
        string="Post-Repair Site Photo Evidence Ref",
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.ref("base.BDT", raise_if_not_found=False)
        or self.env.company.currency_id,
    )
    onsite_collection_amount = fields.Monetary(
        string="On-Site Collection Amount (BDT)",
        currency_field="currency_id",
        default=0.0,
        tracking=True,
        help="FLAW-02.3: Chargeable amount collected on site via MFS or cash.",
    )
    onsite_payment_method = fields.Selection(
        [
            ("none", "Zero-Charge / Covered by Contract"),
            ("cash", "Cash Collected On-Site"),
            ("bkash", "bKash Merchant QR / Payment"),
            ("nagad", "Nagad Merchant QR / Payment"),
            ("sslcommerz", "SSLCOMMERZ Payment Link"),
            ("corporate_credit", "B2B Corporate Credit Billing"),
        ],
        string="On-Site Payment Method",
        default="none",
        tracking=True,
    )
    onsite_payment_trx_id = fields.Char(
        string="bKash / Nagad / SSLCOMMERZ TrxID",
        tracking=True,
        help="FLAW-02.3: Mandatory verified transaction reference for MFS/digital on-site collections.",
    )
    cash_shift_id = fields.Many2one(
        "fix.cash.shift",
        string="Handed Over to Branch Cash Shift (HS-08)",
        tracking=True,
        help="HS-08: Links on-site cash collected by field engineer to the M04 branch cash drawer shift.",
    )
    customer_otp_verified = fields.Boolean(
        string="Customer Handover OTP Verified",
        default=False,
        tracking=True,
    )
    customer_rating = fields.Selection(
        [
            ("5", "5 — Excellent"),
            ("4", "4 — Good"),
            ("3", "3 — Satisfactory"),
            ("2", "2 — Poor"),
            ("1", "1 — Critical Dissatisfaction"),
        ],
        string="On-Site CSAT Rating",
    )
    field_job_sheet_attachment_id = fields.Many2one(
        "ir.attachment",
        string="Signed On-Site Job Sheet (PDF/Photo)",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("operating_unit_id"):
                if vals.get("order_id"):
                    so = self.env["fix.service.order"].browse(vals["order_id"]).exists()
                    if so and so.operating_unit_id:
                        vals["operating_unit_id"] = so.operating_unit_id.id
                if not vals.get("operating_unit_id"):
                    ou = (
                        self.env.user.default_operating_unit_id
                        or self.env["operating.unit"]
                        .sudo()
                        .search(
                            [("company_id", "=", vals.get("company_id", self.env.company.id))],
                            limit=1,
                        )
                        or self.env["operating.unit"].sudo().search([], limit=1)
                    )
                    if ou:
                        vals["operating_unit_id"] = ou.id
            if vals.get("name", "/") == "/":
                seq = self.env["ir.sequence"].next_by_code("fix.field.order")
                vals["name"] = (
                    seq or f"FO/{fields.Date.today().year}/{self.search_count([]) + 1:05d}"
                )
            if not vals.get("name_bn") and vals.get("name"):
                vals["name_bn"] = vals["name"]
            # Start the SLA clock. The service order's own deadline wins; when it
            # carries none, the applicable SLA policy's resolution_hours applies
            # (service type + priority first, then any active policy). Without
            # this the SLA Risk Board had nothing to measure: no deadline was
            # ever written, so the module's SLA screen could only be empty.
            if not vals.get("sla_deadline"):
                deadline = False
                so = (
                    self.env["fix.service.order"].browse(vals["order_id"]).exists()
                    if vals.get("order_id")
                    else None
                )
                if so and so.sla_resolution_deadline:
                    deadline = so.sla_resolution_deadline
                else:
                    Policy = self.env["fix.sla.policy"].sudo()
                    domain = [("active", "=", True)]
                    if so:
                        if so.service_type:
                            domain.append(("service_type", "=", so.service_type))
                        if so.priority:
                            domain.append(("priority", "=", so.priority))
                    policy = Policy.search(domain, limit=1) or Policy.search(
                        [("active", "=", True)], limit=1
                    )
                    if policy and policy.resolution_hours:
                        deadline = fields.Datetime.add(
                            fields.Datetime.now(), hours=policy.resolution_hours
                        )
                if deadline:
                    vals["sla_deadline"] = deadline
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
            van = self.env["fix.stock.location"].search(
                [
                    ("technician_id", "=", rec.technician_id.id),
                    ("is_van_stock", "=", True),
                ],
                limit=1,
            )
            if van:
                rec.van_location_id = van.id

            rec.state = "dispatched"
            rec.dispatched_at = fields.Datetime.now()
            rec._emit_field_event(
                "field.order.dispatched",
                {
                    "field_order_id": rec.id,
                    "order_ref": rec.name,
                    "service_order_ref": rec.order_id.name if rec.order_id else "",
                    "technician_id": rec.technician_id.id,
                    "technician_name": rec.technician_id.name,
                    "zone_id": rec.zone_id.id if rec.zone_id else False,
                    "scheduled_start": rec.scheduled_start.isoformat()
                    if rec.scheduled_start
                    else None,
                },
            )

    def action_accept(self):
        for rec in self:
            if rec.state != "dispatched":
                raise UserError("Only dispatched orders can be accepted.")
            rec.state = "accepted"
            rec.accepted_at = fields.Datetime.now()
            rec._emit_field_event(
                "field.order.accepted",
                {
                    "field_order_id": rec.id,
                    "order_ref": rec.name,
                    "technician_id": rec.technician_id.id if rec.technician_id else False,
                    "accepted_at": fields.Datetime.now().isoformat(),
                },
            )

    def action_decline(self, reason="other", notes=""):
        DeclineLog = self.env["fix.field.decline.log"]
        for rec in self:
            if rec.state != "dispatched":
                raise UserError("Only dispatched orders can be declined.")
            prev_tech = rec.technician_id
            if not prev_tech:
                # the decline log names the declining technician (NOT NULL)
                raise UserError("Only an order dispatched to a technician can be declined.")
            rec.write(
                {
                    "state": "declined",
                    "decline_reason": reason,
                    "decline_notes": notes,
                    "technician_id": False,
                }
            )
            DeclineLog.create(
                {
                    "field_order_id": rec.id,
                    "technician_id": prev_tech.id,
                    "company_id": rec.company_id.id,
                    "operating_unit_id": rec.operating_unit_id.id,
                    "reason": reason,
                    "notes": notes,
                }
            )
            rec._emit_field_event(
                "field.order.declined",
                {
                    "field_order_id": rec.id,
                    "order_ref": rec.name,
                    "declined_technician_id": prev_tech.id,
                    "reason": reason,
                    "notes": notes,
                    "declined_at": fields.Datetime.now().isoformat(),
                },
            )

    def action_start_travel(self):
        for rec in self:
            if rec.state != "accepted":
                raise UserError("Technician must accept the order before starting travel.")
            rec.state = "en_route"
            rec.en_route_at = fields.Datetime.now()

    def action_arrive(self, current_lat=None, current_lon=None, is_mock_location=False):
        for rec in self:
            if rec.state != "en_route":
                raise UserError("Order must be en route to mark arrival.")
            # FLAW-02.2: Hard-block arrival if mock location / GPS spoofing is active
            is_mock = False
            if is_mock_location is True or (
                isinstance(getattr(rec, "is_mock_location", None), bool) and rec.is_mock_location
            ):
                is_mock = True
            elif rec.technician_id and hasattr(self.env, "cr") and hasattr(self.env, "__getitem__"):
                try:
                    if "fix.technician.location" in self.env:
                        res = (
                            self.env["fix.technician.location"]
                            .sudo()
                            .search(
                                [("technician_id", "=", rec.technician_id.id)],
                                order="timestamp desc",
                                limit=1,
                            )
                        )
                        if res and getattr(res, "is_mock_location", False) is True:
                            is_mock = True
                except Exception:
                    # Anti-spoofing evidence: a lookup that errors is not proof
                    # of a genuine location, so it is logged rather than lost.
                    _logger.warning(
                        "GPS mock-location check failed for field order %s", rec.id, exc_info=True
                    )

            if is_mock:
                rec._emit_field_event(
                    "gps.spoofing.blocked",
                    {
                        "field_order_id": rec.id,
                        "order_ref": rec.name,
                        "technician_id": rec.technician_id.id if rec.technician_id else False,
                    },
                )
                raise UserError(
                    f"FLAW-02.2 Anti-Spoofing Gate: Arrival check-in blocked for {rec.name} — "
                    "mock GPS location provider or GNSS spoofing telemetry detected."
                )
            if current_lat is not None and current_lon is not None and rec.geofence_id:
                in_fence = rec._check_geofence_arrival(current_lat, current_lon)
                if not in_fence:
                    rec._emit_field_event(
                        "geofence.breach.detected",
                        {
                            "field_order_id": rec.id,
                            "order_ref": rec.name,
                            "technician_id": rec.technician_id.id if rec.technician_id else False,
                            "current_lat": current_lat,
                            "current_lon": current_lon,
                            "geofence_id": rec.geofence_id.id,
                            "detail": "Arrival recorded outside designated geofence perimeter.",
                        },
                    )
            rec.arrived_at = fields.Datetime.now()
            if rec.en_route_at:
                travelled = (rec.arrived_at - rec.en_route_at).total_seconds() / 60.0
                rec.actual_travel_minutes = round(travelled, 1)
            rec.state = "arrived"

    def action_start_work(self):
        for rec in self:
            if rec.state != "arrived":
                raise UserError("Technician must arrive on site before commencing work.")
            rec.state = "in_progress"
            rec.started_work_at = fields.Datetime.now()

    def action_complete(self):
        for rec in self:
            if rec.state != "in_progress":
                raise UserError("Only in-progress orders can be completed.")
            # FLAW-02.3: Require verified MFS/Gateway TrxID when digital on-site payment is collected
            amt = getattr(rec, "onsite_collection_amount", 0.0)
            if isinstance(amt, int | float) and amt > 0:
                method = getattr(rec, "onsite_payment_method", False)
                trx_id = getattr(rec, "onsite_payment_trx_id", False)
                if method in ("bkash", "nagad", "sslcommerz") and not trx_id:
                    raise UserError(
                        f"FLAW-02.3 On-Site Payment Gate: Order {rec.name} has an MFS/Digital "
                        f"collection of BDT {amt:.2f} via "
                        f"'{method}' without a verified Transaction ID."
                    )
            rec.state = "completed"
            rec.completed_at = fields.Datetime.now()
            if (
                rec.order_id
                and isinstance(amt, int | float)
                and amt > 0
                and rec.onsite_payment_method in ("bkash", "nagad", "sslcommerz", "cash")
            ):
                rec.order_id.write(
                    {
                        "payment_settlement_state": "settled",
                        "invoice_ref": rec.onsite_payment_trx_id or f"COD/{rec.name}",
                        "amount_settled_bdt": amt,
                    }
                )

    def action_handover_field_cash(self, shift_id=None):
        """HS-08: Deposit on-site cash collected by the field engineer into an M04
        branch cash drawer shift (`fix.cash.shift.field_cash_deposited`)."""
        Shift = self.env["fix.cash.shift"]
        for rec in self:
            if rec.onsite_payment_method != "cash" or rec.onsite_collection_amount <= 0:
                raise UserError(
                    f"Order {rec.name} has no on-site cash collection to hand over to a branch shift."
                )
            shift = Shift.browse(shift_id) if shift_id else rec.cash_shift_id
            if not shift:
                shift = Shift.search(
                    [("state", "=", "open"), ("company_id", "=", rec.company_id.id)],
                    order="id desc",
                    limit=1,
                )
            if not shift or not shift.exists():
                raise UserError(
                    "HS-08 Field Cash Handover: No open Branch Cash Shift found to receive field cash."
                )
            rec.cash_shift_id = shift.id
            shift.field_cash_deposited = (
                shift.field_cash_deposited or 0.0
            ) + rec.onsite_collection_amount
            rec.message_post(
                body=f"HS-08: On-site cash BDT {rec.onsite_collection_amount:.2f} handed over to Branch Cash Shift #{shift.id}."
            )

    def action_cancel(self, reason=""):
        for rec in self:
            if rec.state == "completed":
                raise UserError("Completed orders cannot be cancelled.")
            rec.state = "cancelled"
            if reason:
                rec.notes = f"{rec.notes or ''}\nCancellation: {reason}".strip()

    def action_suggest_technicians(self, limit=5):
        """The dispatch suggestion engine (M02): a deterministic, explainable
        ranking — NOT a black-box "AI". For this order's zone and scheduled
        day, technicians score:

          +30  rostered that day (fix.roster.slot — the real availability)
          +25  certification-eligible for the device (FR-LMS-039
               fix.certification.dispatch_eligibility; skills the W2 seam
               left unwired at dispatch time)
          +20  home zone matches the order's dispatch zone (roster branch)
          +15  live GPS proximity (< 5 km: +15, < 15 km: +10, < 30 km: +5; FLAW-02.1)
          +10  assigned active van stock location (FLAW-02.1)
           -5  per already-assigned ACTIVE field order (load)

        Candidates are the employees the business actually dispatches
        (referenced as technicians on work orders, field orders or roster
        slots). Returns a list of dicts sorted best-first; every line carries
        its reasons so the dispatcher decides, the model only recommends.
        """
        self.ensure_one()
        Employee = self.env["hr.employee"]
        FieldOrder = self.env["fix.field.order"]
        Roster = self.env["fix.roster.slot"]
        Certification = self.env["fix.certification"]
        LocationPing = self.env["fix.technician.location"]
        StockLocation = self.env["fix.stock.location"]

        candidate_ids = set()
        for model, field in (
            ("fix.work.order", "technician_id"),
            ("fix.field.order", "technician_id"),
            ("fix.roster.slot", "employee_id"),
        ):
            try:
                candidate_ids.update(
                    self.env[model].sudo().search([(field, "!=", False)]).mapped(field).ids
                )
            except Exception:
                # a source model absent from this database simply contributes
                # no candidates — the others still stand
                _logger.debug("candidate source %s unavailable", model, exc_info=True)
        if not candidate_ids:
            return []

        scheduled_day = (self.scheduled_start or fields.Datetime.now()).date()
        roster_day = Roster.sudo().search([("date", "=", scheduled_day)])
        roster_by_employee = {r.employee_id.id: r for r in roster_day}

        device_type = None
        device = self.order_id.device_id
        if device and device.device_model_id:
            device_type = device.device_model_id.device_type or None

        active_states = ("dispatched", "accepted", "en_route", "arrived", "in_progress")
        load_by_employee = {}
        for fo in FieldOrder.sudo().search(
            [("state", "in", active_states), ("technician_id", "!=", False)]
        ):
            load_by_employee[fo.technician_id.id] = load_by_employee.get(fo.technician_id.id, 0) + 1

        van_tech_ids = set(
            StockLocation.sudo()
            .search([("is_van_stock", "=", True), ("technician_id", "!=", False)])
            .mapped("technician_id")
            .ids
        )

        suggestions = []
        for employee in Employee.browse(candidate_ids).exists():
            reasons = []
            score = 0
            rostered = roster_by_employee.get(employee.id)
            if rostered:
                score += 30
                reasons.append("rostered today")
            eligible, reason = Certification.dispatch_eligibility(employee, device_type)
            if eligible:
                score += 25
                reasons.append("certified")
            elif reason and "no gating" not in reason.lower():
                reasons.append("cert: %s" % reason)
            zone_match = False
            if rostered and rostered.branch_id and rostered.branch_id.zone_id:
                zone_match = rostered.branch_id.zone_id.id == self.zone_id.id
            if zone_match:
                score += 20
                reasons.append("home zone")
            # FLAW-02.1: Live GPS Haversine proximity & van stock availability scoring
            distance_km = None
            if self.latitude and self.longitude:
                ping = LocationPing.sudo().search(
                    [("technician_id", "=", employee.id), ("is_mock_location", "=", False)],
                    order="timestamp desc",
                    limit=1,
                )
                if ping and ping.latitude and ping.longitude:
                    distance_km = round(
                        self._haversine_distance(
                            self.latitude, self.longitude, ping.latitude, ping.longitude
                        )
                        / 1000.0,
                        2,
                    )
                    if distance_km <= 5.0:
                        score += 15
                        reasons.append(f"GPS proximity {distance_km:.1f} km")
                    elif distance_km <= 15.0:
                        score += 10
                        reasons.append(f"GPS proximity {distance_km:.1f} km")
                    elif distance_km <= 30.0:
                        score += 5
                        reasons.append(f"GPS proximity {distance_km:.1f} km")
            has_van_stock = employee.id in van_tech_ids
            if has_van_stock:
                score += 10
                reasons.append("van stock ready")
            open_jobs = load_by_employee.get(employee.id, 0)
            score -= open_jobs * 5
            if open_jobs:
                reasons.append("%d active job(s)" % open_jobs)
            suggestions.append(
                {
                    "employee_id": employee.id,
                    "name": employee.name,
                    "score": score,
                    "eligible": bool(eligible),
                    "rostered": bool(rostered),
                    "zone_match": zone_match,
                    "distance_km": distance_km,
                    "has_van_stock": has_van_stock,
                    "open_jobs": open_jobs,
                    "reasons": reasons,
                }
            )
        suggestions.sort(key=lambda s: (-s["score"], s["open_jobs"], s["name"]))
        return suggestions[:limit]

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
        a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * (
            math.sin(dlam / 2.0) ** 2
        )
        return 2.0 * r * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    def _emit_field_event(self, event_type: str, payload: dict):
        """Emit domain event through the transactional outbox per AS-08 (FF-28).

        The previous body tested ``self.env.get("fix.event.outbox")`` - an EMPTY
        recordset, which is falsy - and would then have called a non-existent
        ``create_event``: no field-order event was ever emitted."""
        publish(self.env, event_type, "fix.field.order", self.id, payload)
