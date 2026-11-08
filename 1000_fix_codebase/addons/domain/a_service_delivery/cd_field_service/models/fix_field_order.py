# fix.field.order — Field Service Order & Execution Unit (CD-M02-01)
import hashlib
import json
import logging
import math

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

# FF-28. A02 audit B2: every event is a literal publish(...) call so FF-48
# sees it; the private _emit_field_event wrapper hid them.
from libs.py.fix_events import publish

_logger = logging.getLogger(__name__)

# A02 audit M02-4/M02-9: dispatch, reassignment and cancellation are dispatcher
# decisions. The group already exists (security/fix_field_service_security.xml).
DISPATCHER_GROUP = "cd_field_service.group_fix_field_service_manager"

# A02 audit M02-2: what completion needs. "strict" (the default, and what any
# unknown value means) requires the customer's sign-off (verified OTP or a
# captured signature), a post-work photo and a work summary. "no_photo" drops
# only the photo, for zones where the business decides a photo cannot be
# taken. The switch is a business decision; the default fails closed.
EVIDENCE_PROFILE_PARAM = "cd_field_service.completion_evidence_profile"
EVIDENCE_PROFILES = ("strict", "no_photo")

# A02 audit M02-4 (P2): a dispatched job nobody accepts goes back to the
# dispatcher after this many minutes. The timeout is a business decision, so
# unset or 0 keeps today's behaviour (no timeout).
ACCEPT_TIMEOUT_PARAM = "cd_field_service.acceptance_timeout_minutes"

MFS_METHODS = ("bkash", "nagad", "sslcommerz")
OPEN_STATES = ("pending_dispatch", "dispatched", "accepted", "en_route", "arrived", "in_progress")

# A02 audit M02-1/M02-10: fields only a transition may change. A technician
# wrote state=completed with customer_otp_verified=True on a dispatched order,
# moved a breached SLA deadline 30 days out and cleared the mock-GPS block.
_GUARDED = frozenset(
    {
        "state",
        "technician_id",
        "sla_deadline",
        "sla_escalated_at",
        # journey stamps (they drive the on-time and travel KPIs)
        "dispatched_at",
        "accepted_at",
        "en_route_at",
        "arrived_at",
        "started_work_at",
        "completed_at",
        "actual_travel_minutes",
        "arrival_latitude",
        "arrival_longitude",
        # anti-spoofing and geofence
        "is_mock_location",
        "geofence_waived_by",
        "geofence_waive_reason",
        # decline / cancel records
        "decline_reason",
        "decline_notes",
        "cancel_reason",
        # completion evidence
        "customer_otp_verified",
        "customer_signature_attachment_id",
        "customer_signature_signer",
        "customer_signature_sha256",
        "customer_signature_at",
        "pre_work_photo_attachment_id",
        "post_work_photo_attachment_id",
        "oem_certification_verified",
        "safety_ppe_verified",
        # on-site money (A02 audit M02-3)
        "onsite_collection_amount",
        "onsite_payment_method",
        "onsite_payment_trx_id",
        "onsite_payment_state",
        "cash_shift_id",
        "cash_handed_over_at",
    }
)

# What a closed (completed or cancelled) order keeps as it was closed: the
# technician's own inputs stay editable while the job runs, not afterwards.
_FROZEN_WHEN_CLOSED = frozenset(
    {
        "order_id",
        "zone_id",
        "geofence_id",
        "priority",
        "scheduled_start",
        "scheduled_end",
        "customer_address",
        "latitude",
        "longitude",
        "work_summary",
        "before_repair_photo_ref",
        "after_repair_photo_ref",
        "field_job_sheet_attachment_id",
        "customer_rating",
        "diagnostic_tool_serial",
    }
)


def _point_in_fence(fence, lat, lon):
    """True when (lat, lon) lies inside ``fence`` (circle or polygon).

    A02 audit M02-8 (P2): a fence whose geometry cannot be read used to test
    True, so a broken (or blanked) fence let any position check in. It now
    tests False: the arrival is refused and the dispatcher either repairs the
    fence or waives it for the order (action_waive_geofence), with a reason."""
    try:
        geom = json.loads(fence.geometry_json or "")
    except (TypeError, ValueError):
        _logger.warning("geofence %s has unreadable geometry", getattr(fence, "id", "?"))
        return False
    if not isinstance(geom, dict):
        _logger.warning("geofence %s geometry is not an object", getattr(fence, "id", "?"))
        return False
    if fence.geofence_type == "circle":
        try:
            center_lat = float(geom["lat"])
            center_lon = float(geom["lng"])
            radius_m = float(geom.get("radius_m", 500.0))
        except (KeyError, TypeError, ValueError):
            _logger.warning("geofence %s circle has no readable centre", getattr(fence, "id", "?"))
            return False
        return FixFieldOrder._haversine_distance(lat, lon, center_lat, center_lon) <= radius_m
    # Polygon ray-casting algorithm
    points = geom.get("points", [])
    if not isinstance(points, list) or len(points) < 3:
        _logger.warning("geofence %s polygon has fewer than 3 points", getattr(fence, "id", "?"))
        return False
    inside = False
    j = len(points) - 1
    for i in range(len(points)):
        xi, yi = points[i][0], points[i][1]
        xj, yj = points[j][0], points[j][1]
        if ((yi > lon) != (yj > lon)) and (lat < (xj - xi) * (lon - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


class FixFieldOrder(models.Model):
    """Field service order executing on-site customer repairs and diagnostics."""

    _name = "fix.field.order"
    _description = "Field Service Order"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
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

    # --- A02 audit P0: the records the transitions keep -------------------
    # M02-2: completion evidence. The signature and photos are attachments
    # that came through the technician's evidence channel (bearer-authenticated,
    # bound to the assigned technician), linked by _fix_attach_field_evidence.
    customer_signature_attachment_id = fields.Many2one(
        "ir.attachment", string="Customer Signature", readonly=True, copy=False
    )
    customer_signature_signer = fields.Char(string="Signed By", readonly=True, copy=False)
    customer_signature_sha256 = fields.Char(string="Signature SHA-256", readonly=True, copy=False)
    customer_signature_at = fields.Datetime(string="Signed At", readonly=True, copy=False)
    pre_work_photo_attachment_id = fields.Many2one(
        "ir.attachment", string="Pre-Work Photo", readonly=True, copy=False
    )
    post_work_photo_attachment_id = fields.Many2one(
        "ir.attachment", string="Post-Work Photo", readonly=True, copy=False
    )
    # M02-3: on-site money is recorded, never settled by the field order.
    onsite_payment_state = fields.Selection(
        [
            ("none", "No On-Site Collection"),
            ("pending_handover", "Cash Pending Hand-over"),
            ("pending_settlement", "Collected, Settlement Not Recorded"),
            ("settled", "Settlement Recorded on the Service Order"),
        ],
        string="On-Site Payment Status",
        default="none",
        required=True,
        tracking=True,
        copy=False,
    )
    cash_handed_over_at = fields.Datetime(string="Cash Handed Over At", readonly=True, copy=False)
    # M02-9: why it was cancelled, and M02-8: a dispatcher's geofence waiver
    cancel_reason = fields.Text(string="Cancellation Reason", readonly=True, copy=False)
    geofence_waived_by = fields.Many2one(
        "res.users", string="Geofence Waived By", readonly=True, copy=False
    )
    geofence_waive_reason = fields.Text(string="Geofence Waiver Reason", readonly=True, copy=False)
    arrival_latitude = fields.Float(
        string="Arrival Latitude", digits=(10, 7), readonly=True, copy=False
    )
    arrival_longitude = fields.Float(
        string="Arrival Longitude", digits=(10, 7), readonly=True, copy=False
    )
    # M02-7: when the breach was escalated to the dispatchers
    sla_escalated_at = fields.Datetime(string="SLA Breach Escalated At", readonly=True, copy=False)

    # ------------------------------------------------------------------ guard
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | _GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(rec.state in ("completed", "cancelled") for rec in self):
            locked = locked | _FROZEN_WHEN_CLOSED
        return locked

    def write(self, vals):
        # A closed order keeps what it was closed with (A02 audit M02-2): the
        # work summary and site details were editable after completion.
        touched = _FROZEN_WHEN_CLOSED & set(vals)
        if touched and not self._fix_guard_open():
            changed = {
                name
                for rec in self
                if rec.state in ("completed", "cancelled")
                for name in touched
                if rec._fix_guard_differs(name, vals[name], rec[name])
            }
            if changed:
                raise UserError(
                    "Cannot change %s on a completed or cancelled field order: it keeps "
                    "what it was closed with."
                    % ", ".join(sorted(self._fields[n].string or n for n in changed))
                )
        return super().write(vals)

    # ------------------------------------------------------- authority checks
    def _fix_is_dispatcher(self) -> bool:
        return self.env.su or self.env.user.has_group(DISPATCHER_GROUP)

    def _fix_require_dispatcher(self, what):
        """A02 audit M02-4/M02-9: dispatch decisions need the dispatcher group."""
        if not self._fix_is_dispatcher():
            raise AccessError(
                "%s is a dispatcher decision. Ask a member of the Field Service "
                "Dispatcher group." % what
            )

    def _fix_require_assigned_technician(self, what):
        """A02 audit M02-4: only the technician the order is dispatched to may
        accept or progress it. Superuser code (the offline sync, which checks
        the assignment itself) is trusted."""
        if self.env.su:
            return
        for rec in self:
            user = rec.sudo().technician_id.user_id
            if not user or user != self.env.user:
                raise AccessError(
                    "Only the technician %s is assigned to can %s it." % (rec.name, what)
                )

    @api.model_create_multi
    def create(self, vals_list):
        # A02 audit M02-7: the SLA deadline is derived here, never typed. An
        # untrusted caller may pass it only when it equals the derived value
        # (the M01 bridge passes the service order's own deadline); the
        # derived value is written through the guard after create.
        trusted = self._fix_guard_open()
        derived = []
        for vals in vals_list:
            supplied = vals.pop("sla_deadline", None) if not trusted else None
            if trusted and vals.get("sla_deadline"):
                derived.append(None)
            else:
                deadline = self._fix_derive_sla_deadline(vals.get("order_id"))
                if supplied and self.browse()._fix_guard_differs(
                    "sla_deadline", supplied, deadline or False
                ):
                    self._fix_guard_refuse(["sla_deadline"])
                derived.append(deadline)
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
        records = super().create(vals_list)
        # Start the SLA clock (written through the guard: an untrusted
        # creator cannot set it, see above).
        for rec, deadline in zip(records, derived, strict=True):
            if deadline:
                rec._guarded().write({"sla_deadline": deadline})
        return records

    def _fix_derive_sla_deadline(self, order_id):
        """The service order's own deadline; else the applicable SLA policy's
        resolution_hours (service type + priority first, then any active
        policy). Without this the SLA Risk Board had nothing to measure: no
        deadline was ever written, so the module's SLA screen was empty."""
        so = self.env["fix.service.order"].browse(order_id).exists() if order_id else None
        if so and so.sla_resolution_deadline:
            return so.sla_resolution_deadline
        Policy = self.env["fix.sla.policy"].sudo()
        domain = [("active", "=", True)]
        if so:
            if so.service_type:
                domain.append(("service_type", "=", so.service_type))
            if so.priority:
                domain.append(("priority", "=", so.priority))
        policy = Policy.search(domain, limit=1) or Policy.search([("active", "=", True)], limit=1)
        if policy and policy.resolution_hours:
            return fields.Datetime.add(fields.Datetime.now(), hours=policy.resolution_hours)
        return False

    def action_request_dispatch(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only draft field orders can be submitted for dispatch.")
            rec._guarded().write({"state": "pending_dispatch"})

    @api.model
    def _fix_resolve_technician(self, technician_id):
        """The hr.employee a dispatch names (the P03 prompt sends a string)."""
        if not technician_id:
            return self.env["hr.employee"]
        if isinstance(technician_id, models.BaseModel):
            return technician_id[:1]
        try:
            emp_id = int(str(technician_id).strip())
        except (TypeError, ValueError):
            raise UserError("Name the technician by their employee id.") from None
        employee = self.env["hr.employee"].sudo().browse(emp_id).exists()
        if not employee:
            raise UserError("Technician %s does not exist." % emp_id)
        return employee

    def action_dispatch(self, technician_id=None):
        # A02 audit M02-4: a plain technician self-dispatched through P03.
        self._fix_require_dispatcher("Dispatching a field order")
        technician = self._fix_resolve_technician(technician_id)
        for rec in self:
            if rec.state not in ("draft", "pending_dispatch", "declined"):
                raise UserError(f"Cannot dispatch order in state '{rec.state}'.")
            tech = technician or rec.technician_id
            if not tech:
                raise UserError("A technician must be assigned to dispatch the field order.")

            vals = {
                "technician_id": tech.id,
                "state": "dispatched",
                "dispatched_at": fields.Datetime.now(),
                "accepted_at": False,
                "en_route_at": False,
            }
            # Check technician van stock location
            van = self.env["fix.stock.location"].search(
                [
                    ("technician_id", "=", tech.id),
                    ("is_van_stock", "=", True),
                ],
                limit=1,
            )
            if van:
                vals["van_location_id"] = van.id
            rec._guarded().write(vals)
            publish(
                rec.env,
                "field.order.dispatched",
                "fix.field.order",
                rec.id,
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

    def action_reassign(self, technician_id=None, reason="", reassignment=None):
        """A02 audit M02-4: a dispatcher moves a dispatched job to another
        technician, with a reason. Technician B took over A's in-progress job
        by editing technician_id on the form; that field is now guarded and
        this is the only way to change it once dispatched. A job already on
        site is not handed over mid-work: cancel it with a reason instead.

        ``reassignment`` is the workspace prompt's one string:
        ``"<employee id> <reason>"``."""
        self._fix_require_dispatcher("Reassigning a field order")
        if reassignment not in (None, "", False):
            head, _sep, tail = str(reassignment).strip().partition(" ")
            technician_id, reason = head, tail
        reason = (reason or "").strip()
        if not reason:
            raise UserError("Give the reason for the reassignment.")
        technician = self._fix_resolve_technician(technician_id)
        if not technician:
            raise UserError("Name the technician to reassign the order to.")
        for rec in self:
            if rec.state not in ("dispatched", "accepted", "en_route"):
                raise UserError(
                    "Only a dispatched, accepted or en-route order can be reassigned "
                    "(%s is %s)." % (rec.name, rec.state)
                )
            previous = rec.technician_id
            if previous == technician:
                raise UserError("%s is already assigned to %s." % (rec.name, technician.name))
            rec._guarded().write(
                {
                    "technician_id": technician.id,
                    "state": "dispatched",
                    "dispatched_at": fields.Datetime.now(),
                    "accepted_at": False,
                    "en_route_at": False,
                    "geofence_waived_by": False,
                    "geofence_waive_reason": False,
                }
            )
            rec.message_post(
                body="Reassigned from %s to %s by %s. Reason: %s"
                % (previous.name or "nobody", technician.name, self.env.user.name, reason)
            )
            publish(
                rec.env,
                "field.order.reassigned",
                "fix.field.order",
                rec.id,
                {
                    "field_order_id": rec.id,
                    "order_ref": rec.name,
                    "previous_technician_id": previous.id,
                    "technician_id": technician.id,
                    "reason": reason,
                },
            )

    def action_accept(self):
        for rec in self:
            if rec.state != "dispatched":
                raise UserError("Only dispatched orders can be accepted.")
            # A02 audit M02-4: technician B accepted A's job.
            rec._fix_require_assigned_technician("accept")
            rec._guarded().write({"state": "accepted", "accepted_at": fields.Datetime.now()})
            publish(
                rec.env,
                "field.order.accepted",
                "fix.field.order",
                rec.id,
                {
                    "field_order_id": rec.id,
                    "order_ref": rec.name,
                    "technician_id": rec.technician_id.id if rec.technician_id else False,
                    "accepted_at": fields.Datetime.now().isoformat(),
                },
            )

    def action_decline(self, reason="other", notes=""):
        """The assigned technician declines a dispatched job, with a reason.
        ``reason`` is a decline code, or free text (then filed as "other")."""
        codes = dict(self._fields["decline_reason"].selection)
        reason = (reason or "").strip() if isinstance(reason, str) else reason
        notes = (notes or "").strip()
        if reason not in codes:
            notes = " ".join(p for p in (str(reason or ""), notes) if p).strip()
            reason = "other"
        # the log is the audit record of this decline: written by this method
        # only (technicians have read-only access to it, A02 audit M02-4)
        DeclineLog = self.env["fix.field.decline.log"].sudo()
        for rec in self:
            if rec.state != "dispatched":
                raise UserError("Only dispatched orders can be declined.")
            prev_tech = rec.technician_id
            if not prev_tech:
                # the decline log names the declining technician (NOT NULL)
                raise UserError("Only an order dispatched to a technician can be declined.")
            rec._fix_require_assigned_technician("decline")
            if reason == "other" and not notes:
                raise UserError("Say why the job is declined.")
            rec._guarded().write(
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
            publish(
                rec.env,
                "field.order.declined",
                "fix.field.order",
                rec.id,
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
            rec._fix_require_assigned_technician("start travel on")
            rec._guarded().write({"state": "en_route", "en_route_at": fields.Datetime.now()})

    @staticmethod
    def _fix_parse_position(position):
        """``"23.81, 90.41"`` -> (23.81, 90.41); the P03 prompt sends one string."""
        if isinstance(position, list | tuple) and len(position) == 2:
            parts = list(position)
        else:
            parts = str(position or "").replace(";", ",").split(",")
            if len(parts) != 2:
                parts = str(position or "").split()
        try:
            lat, lon = (float(str(p).strip()) for p in parts)
        except (TypeError, ValueError):
            raise UserError(
                "Give your position as latitude, longitude (for example 23.8103, 90.4125)."
            ) from None
        if not (math.isfinite(lat) and math.isfinite(lon)) or abs(lat) > 90 or abs(lon) > 180:
            raise UserError("That position is not a valid latitude, longitude.")
        return lat, lon

    def _fix_arrival_fences(self):
        """The fences an arrival is tested against: the order's own customer
        geofence, else the active fences of its dispatch zone."""
        self.ensure_one()
        if self.geofence_id:
            return self.geofence_id.sudo()
        if not self.zone_id:
            return self.env["fix.geofence"]
        return (
            self.env["fix.geofence"]
            .sudo()
            .search([("zone_id", "=", self.zone_id.id), ("active", "=", True)])
        )

    def action_arrive(
        self, current_lat=None, current_lon=None, is_mock_location=False, position=None
    ):
        if position not in (None, "", False) and (current_lat is None or current_lon is None):
            current_lat, current_lon = self._fix_parse_position(position)
        for rec in self:
            if rec.state != "en_route":
                raise UserError("Order must be en route to mark arrival.")
            rec._fix_require_assigned_technician("check in on")
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
                publish(
                    rec.env,
                    "gps.spoofing.blocked",
                    "fix.field.order",
                    rec.id,
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
            # A02 audit M02-8: where the order or its zone has a fence, the
            # arrival must give a position inside it. An arrival 11 km out was
            # accepted, and the workspace button sent no position at all. A
            # dispatcher can waive the fence for one order (action_waive_geofence).
            fences = rec._fix_arrival_fences()
            has_position = current_lat is not None and current_lon is not None
            if fences and not rec.geofence_waived_by:
                if not has_position:
                    raise UserError(
                        "Arrival at %s needs your current position: the order is "
                        "geofenced." % rec.name
                    )
                if not any(_point_in_fence(f, current_lat, current_lon) for f in fences):
                    raise UserError(
                        "Arrival refused: your position (%.5f, %.5f) is outside the "
                        "geofence of %s. Check in from the customer site, or ask a "
                        "dispatcher to waive the geofence for this order."
                        % (current_lat, current_lon, rec.name)
                    )
            now = fields.Datetime.now()
            vals = {"state": "arrived", "arrived_at": now}
            if has_position:
                vals.update({"arrival_latitude": current_lat, "arrival_longitude": current_lon})
            if rec.en_route_at:
                travelled = (now - rec.en_route_at).total_seconds() / 60.0
                vals["actual_travel_minutes"] = round(travelled, 1)
            rec._guarded().write(vals)

    def action_waive_geofence(self, reason=""):
        """A02 audit M02-8: a dispatcher lets one order check in without the
        geofence test (a wrong geocode, a customer who moved), with a reason."""
        self._fix_require_dispatcher("Waiving the arrival geofence")
        reason = (reason or "").strip()
        if not reason:
            raise UserError("Give the reason for waiving the geofence.")
        for rec in self:
            if rec.state not in ("dispatched", "accepted", "en_route"):
                raise UserError("The geofence can be waived only before arrival.")
            rec._guarded().write(
                {"geofence_waived_by": self.env.user.id, "geofence_waive_reason": reason}
            )
            rec.message_post(
                body="Arrival geofence waived by %s. Reason: %s" % (self.env.user.name, reason)
            )

    def action_start_work(self):
        for rec in self:
            if rec.state != "arrived":
                raise UserError("Technician must arrive on site before commencing work.")
            rec._fix_require_assigned_technician("start work on")
            rec._guarded().write({"state": "in_progress", "started_work_at": fields.Datetime.now()})

    # ------------------------------------------------------ on-site evidence
    def _fix_attach_field_evidence(self, attachment, media_type, signer=None):
        """Link an evidence attachment (signature or photo) to this order.

        Called by the technician's evidence channel and the offline signature
        op (both bound to the assigned technician), never over RPC: the name
        is private. A02 audit M02-2: the signature op answered verified=True
        and stored only a chatter line with a client token."""
        self.ensure_one()
        attachment = attachment.sudo()
        if attachment.res_model != self._name or attachment.res_id != self.id:
            raise UserError("That attachment does not belong to field order %s." % self.name)
        media_type = (media_type or "photo").lower()
        vals = {}
        if media_type == "signature":
            if self.state not in ("arrived", "in_progress"):
                raise UserError("The customer signs on site: %s is %s." % (self.name, self.state))
            raw = attachment.raw or b""
            if not raw:
                raise UserError("The signature attachment is empty.")
            vals = {
                "customer_signature_attachment_id": attachment.id,
                "customer_signature_signer": (signer or "").strip() or False,
                "customer_signature_sha256": hashlib.sha256(raw).hexdigest(),
                "customer_signature_at": fields.Datetime.now(),
            }
        elif media_type in ("photo", "pre_work_photo", "post_work_photo"):
            if not (attachment.mimetype or "").startswith("image/"):
                return False
            if media_type == "post_work_photo" or (
                media_type == "photo" and self.state == "in_progress"
            ):
                if self.state != "in_progress":
                    raise UserError("A post-work photo is taken while the work is in progress.")
                vals = {"post_work_photo_attachment_id": attachment.id}
            elif self.state in ("arrived", "in_progress") and not self.pre_work_photo_attachment_id:
                vals = {"pre_work_photo_attachment_id": attachment.id}
        if vals:
            self._guarded().write(vals)
        return bool(vals)

    def _fix_completion_evidence_missing(self):
        """What completion still needs, in plain words (empty = complete)."""
        self.ensure_one()
        profile = (
            self.env["ir.config_parameter"].sudo().get_param(EVIDENCE_PROFILE_PARAM) or "strict"
        )
        if profile not in EVIDENCE_PROFILES:
            profile = "strict"  # an unknown value fails closed
        missing = []
        if not (self.customer_otp_verified or self.customer_signature_attachment_id):
            missing.append("the customer's sign-off (a verified OTP or a captured signature)")
        if profile != "no_photo" and not self.post_work_photo_attachment_id:
            missing.append("at least one post-work photo")
        if not (self.work_summary or "").strip():
            missing.append("a work summary")
        return missing

    # -------------------------------------------------------- on-site money
    @api.model
    def _fix_parse_collection(self, payment):
        """``"bkash 1500 8N7A6B5C"`` or ``"cash 900"`` -> (method, amount, trx)."""
        parts = str(payment or "").replace(",", " ").split()
        if len(parts) < 2:
            raise UserError(
                "Give the collection as: method amount [TrxID], for example "
                "'bkash 1500 8N7A6B5C' or 'cash 900'."
            )
        try:
            amount = float(parts[1])
        except ValueError:
            raise UserError("The amount must be a number.") from None
        return parts[0].lower(), amount, (parts[2] if len(parts) > 2 else None)

    def action_record_collection(self, amount=None, method=None, trx_id=None, payment=None):
        """The assigned technician records what was collected on site.

        A02 audit M02-3: the amount, channel and TrxID were plain fields and
        completion settled the service order from them. They are recorded here
        and only here; nothing about the record settles anything."""
        if payment not in (None, "", False):
            method, amount, trx_id = self._fix_parse_collection(payment)
        methods = dict(self._fields["onsite_payment_method"].selection)
        if method not in methods:
            raise UserError("Unknown payment channel '%s'." % (method or ""))
        try:
            amount = float(amount or 0.0)
        except (TypeError, ValueError):
            raise UserError("The amount must be a number.") from None
        if not math.isfinite(amount) or amount < 0:
            raise UserError("The amount must be zero or more.")
        if method == "none" and amount:
            raise UserError("A zero-charge job collects nothing.")
        trx_id = (trx_id or "").strip() or False
        if method in MFS_METHODS and amount > 0 and not trx_id:
            raise UserError(
                f"FLAW-02.3 On-Site Payment Gate: a {methods[method]} collection needs its "
                "Transaction ID."
            )
        for rec in self:
            if rec.state not in ("arrived", "in_progress"):
                raise UserError("A collection is recorded on site, before completion.")
            rec._fix_require_assigned_technician("record a collection on")
            rec._guarded().write(
                {
                    "onsite_collection_amount": amount,
                    "onsite_payment_method": method,
                    "onsite_payment_trx_id": trx_id if method in MFS_METHODS else False,
                }
            )

    def _fix_record_order_settlement(self, amount, reference):
        """Hand the collection to the service order's own settlement method
        (contract with M01: fix.service.order._fix_record_settlement). The
        field order never writes the order's settlement fields itself (A02
        audit M02-3). Returns the payment state to record."""
        self.ensure_one()
        order = self.order_id
        if not order or not hasattr(order, "_fix_record_settlement"):
            self.message_post(
                body="On-site collection of BDT %.2f (%s) recorded; the service order's "
                "settlement was not recorded because its settlement method is not "
                "available." % (amount, reference)
            )
            return "pending_settlement"
        try:
            with self.env.cr.savepoint():
                order._fix_record_settlement(amount, reference, source="field_collection")
        except (UserError, AccessError) as exc:
            self.message_post(
                body="On-site collection of BDT %.2f (%s) recorded; the service order "
                "refused the settlement: %s" % (amount, reference, exc.args[0] if exc.args else exc)
            )
            return "pending_settlement"
        return "settled"

    def action_complete(self):
        for rec in self:
            if rec.state != "in_progress":
                raise UserError("Only in-progress orders can be completed.")
            rec._fix_require_assigned_technician("complete")
            # FLAW-02.3: Require verified MFS/Gateway TrxID when digital on-site payment is collected
            amt = getattr(rec, "onsite_collection_amount", 0.0)
            method = getattr(rec, "onsite_payment_method", False)
            if isinstance(amt, int | float) and amt > 0:
                trx_id = getattr(rec, "onsite_payment_trx_id", False)
                if method in MFS_METHODS and not trx_id:
                    raise UserError(
                        f"FLAW-02.3 On-Site Payment Gate: Order {rec.name} has an MFS/Digital "
                        f"collection of BDT {amt:.2f} via "
                        f"'{method}' without a verified Transaction ID."
                    )
            # A02 audit M02-2 / URD US-P3-013: completion needs the customer's
            # sign-off, a post-work photo and a work summary.
            missing = rec._fix_completion_evidence_missing()
            if missing:
                raise UserError(
                    "Field order %s cannot be completed without %s."
                    % (rec.name, "; ".join(missing))
                )
            # A02 audit M02 step 7 (P2): every part picked for the job is
            # either fitted or returned before the job closes.
            unresolved = rec._fix_parts_unresolved()
            if unresolved:
                raise UserError(
                    "Field order %s cannot be completed: %d picked part(s) are neither "
                    "fitted nor returned (%s)."
                    % (
                        rec.name,
                        len(unresolved),
                        ", ".join(
                            p.part_number or p.product_id.display_name or "?" for p in unresolved
                        ),
                    )
                )
            rec._guarded().write({"state": "completed", "completed_at": fields.Datetime.now()})
            # A02 audit M02-3: completion no longer marks the service order
            # settled. Cash waits for its hand-over to a branch shift; a digital
            # collection goes to the service order's own settlement method.
            pay_state = "none"
            if isinstance(amt, int | float) and amt > 0:
                if method == "cash":
                    pay_state = "pending_handover"
                elif method in MFS_METHODS:
                    pay_state = rec._fix_record_order_settlement(amt, rec.onsite_payment_trx_id)
            rec._guarded().write({"onsite_payment_state": pay_state})
            # A02 audit B2 / M02-11: the hand-back to M01. The order never
            # moved when its field job completed and nothing was published.
            # Contract with the M01 consumer (stream S1): service_order_id
            # (int, or False) and the source record id.
            consumed = rec.sudo().part_line_ids.filtered(lambda ln: ln.state == "consumed")
            publish(
                rec.env,
                "field.order.completed",
                "fix.field.order",
                rec.id,
                {
                    "field_order_id": rec.id,
                    "order_ref": rec.name,
                    "service_order_id": rec.order_id.id or False,
                    "service_order_ref": rec.order_id.name or "",
                    "technician_id": rec.technician_id.id or False,
                    "completed_at": rec.completed_at.isoformat() if rec.completed_at else None,
                    "onsite_payment_state": pay_state,
                    "onsite_collection_amount": amt if isinstance(amt, int | float) else 0.0,
                    "parts_fitted": len(consumed),
                    "parts_total": sum(consumed.mapped("subtotal")),
                },
            )

    def action_handover_field_cash(self, shift_id=None):
        """HS-08: Deposit on-site cash collected by the field engineer into an M04
        branch cash drawer shift (`fix.cash.shift.field_cash_deposited`).

        A02 audit M02-3: the cash is settled on the service order only now,
        when it reaches an open branch shift, and only once."""
        Shift = self.env["fix.cash.shift"].sudo()
        for rec in self:
            if rec.onsite_payment_method != "cash" or rec.onsite_collection_amount <= 0:
                raise UserError(
                    f"Order {rec.name} has no on-site cash collection to hand over to a branch shift."
                )
            if rec.state != "completed" or rec.onsite_payment_state != "pending_handover":
                raise UserError(
                    f"Order {rec.name} has no cash pending hand-over "
                    f"(payment status: {rec.onsite_payment_state})."
                )
            if not rec._fix_is_dispatcher():
                rec._fix_require_assigned_technician("hand over the cash of")
            shift = Shift.browse(int(shift_id)).exists() if shift_id else Shift.browse()
            if not shift:
                shift = Shift.search(
                    [("state", "=", "open"), ("company_id", "=", rec.company_id.id)],
                    order="id desc",
                    limit=1,
                )
            if not shift or shift.state != "open":
                raise UserError(
                    "HS-08 Field Cash Handover: No open Branch Cash Shift found to receive field cash."
                )
            if shift.company_id != rec.company_id:
                raise UserError("The cash shift belongs to another company.")
            # Contract with M04 (A02 audit M04-4): the drawer totals are
            # guarded; the shift's own method posts onto an OPEN shift only.
            shift._post_field_cash(rec.onsite_collection_amount)
            rec._guarded().write(
                {"cash_shift_id": shift.id, "cash_handed_over_at": fields.Datetime.now()}
            )
            rec.message_post(
                body=f"HS-08: On-site cash BDT {rec.onsite_collection_amount:.2f} handed over to Branch Cash Shift #{shift.id}."
            )
            pay_state = rec._fix_record_order_settlement(
                rec.onsite_collection_amount, f"COD/{rec.name}"
            )
            rec._guarded().write({"onsite_payment_state": pay_state})

    def action_cancel(self, reason=""):
        """A02 audit M02-9: a technician cancelled an in-progress job with no
        reason. A reason is required, and once the order is in dispatch the
        cancellation is a dispatcher decision."""
        for rec in self:
            if rec.state == "completed":
                raise UserError("Completed orders cannot be cancelled.")
            if rec.state == "cancelled":
                raise UserError("Order %s is already cancelled." % rec.name)
        reason = (reason or "").strip() if isinstance(reason, str) else ""
        if not reason:
            raise UserError("Give the reason for the cancellation.")
        if any(rec.state != "draft" for rec in self):
            self._fix_require_dispatcher("Cancelling a field order in dispatch")
        for rec in self:
            rec._guarded().write(
                {
                    "state": "cancelled",
                    "cancel_reason": reason,
                    "notes": f"{rec.notes or ''}\nCancellation: {reason}".strip(),
                }
            )

    # ------------------------------------------------------------- SLA watch
    @api.model
    def _cron_escalate_sla_breaches(self, limit=200):
        """A02 audit M02-7: no one was told when a field order passed its SLA
        deadline (42 open orders were past it). Each newly breached open order
        gets one to-do activity for a dispatcher (round robin), once."""
        orders = self.sudo().search(
            [
                ("state", "in", OPEN_STATES),
                ("sla_deadline", "!=", False),
                ("sla_deadline", "<", fields.Datetime.now()),
                ("sla_escalated_at", "=", False),
            ],
            order="sla_deadline asc, id asc",
            limit=limit,
        )
        if not orders:
            return 0
        group = self.env.ref(DISPATCHER_GROUP, raise_if_not_found=False)
        dispatchers = (
            group.sudo().all_user_ids.filtered(lambda u: u.active and not u.share).sorted("id")
            if group
            else self.env["res.users"]
        )
        if not dispatchers:
            _logger.warning(
                "%d field orders are past their SLA deadline and no dispatcher is "
                "appointed to be told.",
                len(orders),
            )
            return 0
        activity_type = self.env.ref("mail.mail_activity_data_todo", raise_if_not_found=False)
        today = fields.Date.context_today(self)
        for i, order in enumerate(orders):
            user = dispatchers[i % len(dispatchers)]
            order.activity_schedule(
                activity_type_id=activity_type.id if activity_type else False,
                summary="SLA breached: %s" % order.name,
                note="Field order %s passed its SLA deadline (%s) in state %s."
                % (order.name, order.sla_deadline, order.state),
                user_id=user.id,
                date_deadline=today,
            )
        orders.write({"sla_escalated_at": fields.Datetime.now()})
        return len(orders)

    @api.model
    def _fix_acceptance_timeout_minutes(self) -> float:
        raw = self.env["ir.config_parameter"].sudo().get_param(ACCEPT_TIMEOUT_PARAM)
        try:
            minutes = float(raw or 0.0)
        except (TypeError, ValueError):
            _logger.warning(
                "%s=%r is not a number; the acceptance timeout is off", ACCEPT_TIMEOUT_PARAM, raw
            )
            return 0.0
        return minutes if math.isfinite(minutes) and minutes > 0 else 0.0

    @api.model
    def _cron_return_unaccepted(self, limit=200):
        """A02 audit M02-4 (P2): a job dispatched to a technician who never
        accepts it sat in 'dispatched' for good; only the SLA cron looked at
        it, once it had already breached. After the acceptance timeout the
        order goes back to pending dispatch, unassigned, with a to-do for a
        dispatcher. Off unless the timeout switch is set."""
        minutes = self._fix_acceptance_timeout_minutes()
        if not minutes:
            return 0
        cutoff = fields.Datetime.subtract(fields.Datetime.now(), minutes=minutes)
        orders = self.sudo().search(
            [("state", "=", "dispatched"), ("dispatched_at", "<", cutoff)],
            order="dispatched_at asc, id asc",
            limit=limit,
        )
        group = self.env.ref(DISPATCHER_GROUP, raise_if_not_found=False)
        dispatchers = (
            group.sudo().all_user_ids.filtered(lambda u: u.active and not u.share).sorted("id")
            if group
            else self.env["res.users"]
        )
        activity_type = self.env.ref("mail.mail_activity_data_todo", raise_if_not_found=False)
        today = fields.Date.context_today(self)
        returned = 0
        for i, order in enumerate(orders):
            try:
                with self.env.cr.savepoint():
                    previous = order.technician_id
                    order._guarded().write(
                        {
                            "state": "pending_dispatch",
                            "technician_id": False,
                            "dispatched_at": False,
                            "geofence_waived_by": False,
                            "geofence_waive_reason": False,
                        }
                    )
                    note = (
                        "Not accepted by %s within %.0f minutes of dispatch: returned to "
                        "the dispatcher." % (previous.name or "the technician", minutes)
                    )
                    order.message_post(body=note)
                    if dispatchers:
                        order.activity_schedule(
                            activity_type_id=activity_type.id if activity_type else False,
                            summary="Re-dispatch: %s" % order.name,
                            note=note,
                            user_id=dispatchers[i % len(dispatchers)].id,
                            date_deadline=today,
                        )
                    returned += 1
            except Exception:
                _logger.exception("acceptance timeout: could not return field order %s", order.id)
        return returned

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
            # the same question the dispatch gate asks, brand and waiver included
            reason = self._fix_certification_problem(employee)
            eligible = not reason
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
        """Validate if current coordinates fall within the assigned geofence.
        A fence with blank geometry fails closed (A02 audit M02-8, P2)."""
        if not self.geofence_id:
            return True
        return _point_in_fence(self.geofence_id, lat, lon)

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
