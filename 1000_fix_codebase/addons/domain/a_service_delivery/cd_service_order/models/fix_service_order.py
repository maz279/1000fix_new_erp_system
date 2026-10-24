# fix.service.order — the flagship model (P04-M03-T02, CD-M01-01).
# Full state machine per AS-06 (declared in ONE place, DP-01).
# SLA computation delegated to services/sla-engine/ (AR-007 section 3.1).
import logging
import uuid

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

logger = logging.getLogger(__name__)

# AS-06: the ONE place the state machine is declared (DP-01)
SERVICE_ORDER_STATES = [
    ("draft", "Draft"),
    ("intake", "Intake — Walk-in/Collection"),
    ("diagnostic", "Diagnostic"),
    ("estimate_pending", "Estimate Pending"),
    ("estimate_sent", "Estimate Sent to Customer"),
    ("awaiting_approval", "Awaiting Customer Approval"),
    ("approved", "Approved — Queued for Repair"),
    ("in_repair", "In Repair"),
    ("qc_pending", "QC Pending"),
    ("qc_failed", "QC Failed — Rework"),
    ("ready", "Ready for Collection"),
    ("delivered", "Delivered"),
    ("closed", "Closed"),
    ("cancelled", "Cancelled"),
]

# State transition map (DP-01: the single authority)
VALID_TRANSITIONS = {
    "draft": {"intake"},
    "intake": {"diagnostic", "cancelled"},
    "diagnostic": {"estimate_pending", "cancelled"},
    "estimate_pending": {"estimate_sent", "cancelled"},
    "estimate_sent": {"awaiting_approval", "cancelled"},
    "awaiting_approval": {"approved", "cancelled"},
    "approved": {"in_repair", "cancelled"},
    "in_repair": {"qc_pending", "cancelled"},
    "qc_pending": {"ready", "qc_failed"},
    "qc_failed": {"in_repair"},
    "ready": {"delivered"},
    "delivered": {"closed"},
    "closed": set(),
    "cancelled": set(),
}


class FixServiceOrder(models.Model):
    """A service order — the primary transacting record of the business.

    Every device that enters a 1000FiX branch gets a service order. The
    full lifecycle from intake to delivery is tracked through this model.
    """

    _name = "fix.service.order"
    _description = "Service Order"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    # AS-03
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)

    # Identity
    name = fields.Char(
        string="Order Reference",
        readonly=True,
        index=True,
        copy=False,
        help="Assigned from the fix.service.order sequence in create(); a missing "
        "sequence is an error, never a shared placeholder reference.",
    )
    idempotency_key = fields.Char(
        string="Idempotency Key",
        index=True,
        copy=False,
        help="DI-04: a retried POST must not create two orders",
    )

    # The device (M17 registry)
    device_id = fields.Many2one(
        "fix.device", string="Device", required=True, ondelete="restrict", index=True
    )
    device_serial = fields.Char(related="device_id.serial_number", store=True, string="S/N")

    # The customer (M33 party kernel)
    customer_id = fields.Many2one(
        "res.partner", string="Customer", required=True, ondelete="restrict", index=True
    )
    customer_phone = fields.Char(related="customer_id.phone", string="Phone")

    # Branch and assignment
    branch_id = fields.Many2one("fix.branch", string="Branch", required=True, ondelete="restrict")
    technician_id = fields.Many2one("hr.employee", string="Assigned Technician")

    # State machine (AS-06/DP-01: the declared transitions above are the authority)
    state = fields.Selection(
        SERVICE_ORDER_STATES,
        default="draft",
        required=True,
        tracking=True,
        index=True,
        group_expand="_read_group_states",
    )

    # Service details
    service_type = fields.Selection(
        [
            ("walk_in", "Walk-in"),
            ("collection", "Collection/Delivery"),
            ("onsite", "On-site"),
            ("mail_in", "Mail-in"),
            ("corporate", "Corporate/Bulk"),
        ],
        required=True,
        default="walk_in",
        tracking=True,
    )
    # BRU-SRM-02/03: the commercial classification gating creation
    order_category = fields.Selection(
        [
            ("standard", "Standard (Paid)"),
            ("warranty", "Warranty"),
            ("amc", "AMC / Contract"),
            ("rework", "Rework"),
            ("rental", "Rental Asset Service"),
            ("refurbishment", "Refurbishment Intake"),
            ("recycling", "Recycling / E-Waste"),
            ("goodwill", "Goodwill (Zero-Charge)"),
        ],
        string="Order Category",
        default="standard",
        required=True,
        tracking=True,
        help="Commercial classification gating order workflow (BRU-SRM-02/03 & W2 business lines)",
    )
    is_rework = fields.Boolean(
        string="Rework",
        default=False,
        copy=False,
        tracking=True,
        help="BRU-SRM-06: auto-flagged when the same device returns with the same "
        "fault within 30 days; linked to the original order",
    )
    rework_of_id = fields.Many2one(
        "fix.service.order", string="Rework Of", copy=False, index=True, readonly=True
    )
    fault_description = fields.Text(string="Fault Description", required=True, tracking=True)
    catalog_item_id = fields.Many2one("fix.catalogue.item", string="Service Catalogue Item")
    priority = fields.Selection(
        [("normal", "Normal"), ("high", "High"), ("urgent", "Urgent"), ("emergency", "Emergency")],
        default="normal",
        required=True,
        tracking=True,
    )

    # FR-SRM-080: Priority Override Logging
    priority_override_reason = fields.Text(string="Priority Override Justification", tracking=True)
    priority_override_user_id = fields.Many2one("res.users", string="Priority Overridden By")

    # FR-SRM-081: Customer-Preferred Technician
    preferred_technician_id = fields.Many2one("hr.employee", string="Customer-Preferred Technician")

    # FR-SRM-082: Repeat-Visit Case Linkage
    parent_case_id = fields.Many2one(
        "fix.service.order", string="Parent Customer Problem Case", index=True
    )
    linked_order_ids = fields.One2many(
        "fix.service.order", "parent_case_id", string="Linked Visit Orders"
    )

    # Currency
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.ref("base.BDT", raise_if_not_found=False)
        or self.env.company.currency_id,
    )

    # --- W2 Business-Line Extensions (FR-SRM-063..088) ---
    # FR-SRM-063: Rental Service Intake
    is_rental = fields.Boolean(string="Rental Intake", default=False, tracking=True)
    rental_agreement_ref = fields.Char(string="Rental Agreement Ref", tracking=True)
    rental_deposit_bdt = fields.Monetary(
        string="Rental Deposit (BDT)", currency_field="currency_id", default=0.0
    )
    rental_liability_bdt = fields.Monetary(
        string="Rental Liability (BDT)", currency_field="currency_id", default=0.0
    )
    rental_start_date = fields.Date(string="Rental Start Date")
    rental_end_date = fields.Date(string="Rental End Date")

    # FR-SRM-064: Rental Swap-Out
    is_swap_out = fields.Boolean(string="Swap-Out Triggered", default=False, tracking=True)
    swap_device_id = fields.Many2one("fix.device", string="Replacement Swap Device", tracking=True)
    swap_reason = fields.Selection(
        [
            ("unrepairable", "Irreparable Fault"),
            ("sla_breach_risk", "Expedited SLA Swap"),
            ("customer_request", "Customer Preference"),
        ],
        string="Swap Reason",
    )
    swap_condition_grade = fields.Selection(
        [
            ("grade_a", "Grade A (Like New)"),
            ("grade_b", "Grade B (Minor Blemishes)"),
            ("grade_c", "Grade C (Functional)"),
        ],
        string="Swap Condition Grade",
    )
    swap_logistics_status = fields.Selection(
        [
            ("pending", "Pending Dispatch"),
            ("dispatched", "In Transit"),
            ("completed", "Device Swapped & Signed"),
        ],
        string="Swap Logistics Status",
        default="pending",
    )

    # Deferred Repair Block
    is_deferred_block = fields.Boolean(string="Deferred Repair Hold", default=False, tracking=True)
    deferred_reason = fields.Selection(
        [
            ("parts_backorder", "Parts Backorder (Supply Chain Hold)"),
            ("customer_travel", "Customer Unavailable / Travel"),
            ("disputed_liability", "Liability / Estimate Dispute"),
            ("third_party_vendor", "OEM Escalation Hold"),
        ],
        string="Deferred Reason",
    )
    deferred_until = fields.Date(string="Deferred Resumption Date", tracking=True)
    deferred_notes = fields.Text(string="Deferred Hold Justification")

    # FR-SRM-065: Data Services Case Intake
    is_data_service = fields.Boolean(string="Data Recovery / Migration", default=False)
    data_confidentiality_level = fields.Selection(
        [
            ("standard", "Standard Commercial"),
            ("confidential", "Confidential"),
            ("strict_nda", "Strict NDA / Legal Hold"),
        ],
        default="standard",
        string="Confidentiality Level",
    )
    data_retention_days = fields.Integer(string="Data Retention Window (Days)", default=14)

    # FR-SRM-066: Refurbishment Work Order Intake
    is_refurbishment = fields.Boolean(string="Refurbishment Intake", default=False)
    refurb_source = fields.Selection(
        [
            ("trade_in", "Customer Trade-in"),
            ("unrepairable_scrap", "Unrepairable Conversion"),
            ("rental_retirement", "Rental Fleet Retirement"),
        ],
        string="Refurbishment Source",
    )
    target_grade = fields.Selection(
        [("grade_a", "Grade A"), ("grade_b", "Grade B"), ("grade_c", "Grade C")],
        string="Target Grade",
    )

    # FR-SRM-067: Recycling Intake
    is_recycling = fields.Boolean(string="E-Waste / Recycling Intake", default=False)
    disposition_triage = fields.Selection(
        [
            ("parts_harvest", "Component / Parts Harvesting"),
            ("metals_recovery", "Metals & PCB Recovery"),
            ("safe_destruction", "Certified Data & Device Destruction"),
        ],
        string="Disposition Triage",
    )
    e_waste_cert_ref = fields.Char(string="E-Waste Green Certificate Ref")

    # FR-SRM-075: Goodwill Repair
    is_goodwill = fields.Boolean(
        string="Goodwill Repair (Zero-Charge)", default=False, tracking=True
    )
    goodwill_cost_attribution_bdt = fields.Monetary(
        string="Goodwill Cost Absorbed (BDT)",
        currency_field="currency_id",
        default=0.0,
    )
    goodwill_approved_by = fields.Many2one("res.users", string="Goodwill Approved By")

    # FR-SRM-076: Loan Device Management
    loan_device_id = fields.Many2one("fix.device", string="Temporary Loan Device")
    loan_issued_at = fields.Datetime(string="Loan Issued At")
    loan_returned_at = fields.Datetime(string="Loan Returned At")
    loan_condition = fields.Char(string="Loan Device Return Condition")

    # FR-SRM-077: Multi-Fault Handling Lines
    fault_line_ids = fields.One2many(
        "fix.service.order.fault", "order_id", string="Fault Diagnosis Lines"
    )

    # SLA (T04: clocks and escalation — computation in services/sla-engine/)
    sla_policy_id = fields.Many2one("fix.sla.policy", string="SLA Policy")
    sla_response_deadline = fields.Datetime(readonly=True)
    sla_resolution_deadline = fields.Datetime(readonly=True)
    sla_response_at = fields.Datetime(readonly=True)
    sla_resolution_at = fields.Datetime(readonly=True)
    sla_clock_paused = fields.Boolean(
        default=False, help="Clock paused during customer hold or parts wait"
    )

    # Related records
    estimate_ids = fields.One2many("fix.estimate", "order_id", string="Estimates")
    work_order_ids = fields.One2many("fix.work.order", "order_id", string="Work Orders")
    qc_checklist_ids = fields.One2many("fix.qc.checklist", "order_id", string="QC Checklists")

    # MIG-03: legacy reference (permanent)
    legacy_reference = fields.Char(
        string="Legacy Reference",
        index=True,
        help="MIG-03: the legacy system's order number, permanently retained",
    )

    active = fields.Boolean(default=True)

    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _idempotency_key_unique = models.Constraint(
        "UNIQUE (idempotency_key)",
        "An order with this idempotency key already exists (DI-04 idempotency).",
    )
    _name_unique = models.Constraint(
        "UNIQUE (name)",
        "Service order references must be unique.",
    )

    @api.model
    def _read_group_states(self, states, domain, order):
        return [state[0] for state in SERVICE_ORDER_STATES]

    # --- State machine enforcement (AS-06/DP-01) ---
    def _validate_transition(self, new_state: str) -> None:
        self.ensure_one()
        old = self.state
        if new_state == old:
            return
        valid_targets = VALID_TRANSITIONS.get(old, set())
        if new_state not in valid_targets:
            raise ValidationError(
                f"Invalid state transition: {old} -> {new_state}. "
                f"Valid transitions from '{old}': {', '.join(sorted(valid_targets)) or '(terminal state)'}"
            )
        if new_state == "ready":
            # BRU-SRM-04 (H): the QC hard gate lives in the transition check
            # so NO write path (action, controller, sync, RPC) reaches Ready
            # without a passed checklist.
            self._check_qc_gate()

    def _check_qc_gate(self) -> None:
        """BRU-SRM-04 (H): an order cannot reach Ready without a PASSED
        quality checklist — a hard gate, not a warning."""
        self.ensure_one()
        checklists = self.qc_checklist_ids
        if not checklists:
            raise UserError(
                "Order %s has no QC checklist — Ready requires one (BRU-SRM-04)" % self.name
            )
        failed = checklists.filtered(lambda c: c.state != "passed")
        if failed:
            raise UserError(
                "Order %s cannot be Ready: %d QC checklist(s) not passed (BRU-SRM-04)"
                % (self.name, len(failed))
            )

    def write(self, vals):
        old_states = {}
        if "state" in vals:
            for rec in self:
                rec._validate_transition(vals["state"])
                old_states[rec.id] = rec.state
        result = super().write(vals)
        if "state" in vals:
            for rec in self:
                rec._on_state_change(vals["state"], old_states[rec.id])
        return result

    def _on_state_change(self, new_state: str, old_state: str) -> None:
        """Hook for side effects on state changes. ``old_state`` is captured
        before the write: reading ``self.state`` here (after it) recorded every
        history entry as "<new> -> <new>"."""
        self._emit(f"service_order.{new_state}", self)
        self.device_id.add_history(
            "service_order", f"Order {self.name}: {old_state} -> {new_state}", order_id=self.id
        )
        # SLA clock events
        if new_state == "in_repair" and not self.sla_response_at:
            self.sla_response_at = fields.Datetime.now()
        if new_state in ("delivered", "closed") and not self.sla_resolution_at:
            self.sla_resolution_at = fields.Datetime.now()

    def action_start_diagnostic(self):
        self.state = "diagnostic"

    def action_send_estimate(self):
        self.state = "estimate_sent"

    def action_approve(self):
        self.state = "approved"

    def action_start_repair(self):
        self.state = "in_repair"

    def action_submit_qc(self):
        self.state = "qc_pending"

    def action_ready(self):
        """BRU-SRM-04 (H): an order cannot reach Ready without a PASSED
        quality checklist — a hard gate, not a warning. Enforced by
        _validate_transition (write), so every path shares the one gate."""
        for order in self:
            order._check_qc_gate()
        self.state = "ready"

    def action_deliver(self):
        self.state = "delivered"

    def action_close(self):
        self.state = "closed"

    def action_cancel(self):
        self.state = "cancelled"

    # --- W2 Business-Line Actions ---
    def action_swap_device(self, replacement_device_id, reason="unrepairable", grade="grade_a"):
        """FR-SRM-064: Convert an irreparable fault or SLA risk into an asset swap."""
        self.ensure_one()
        replacement = self.env["fix.device"].browse(replacement_device_id)
        if not replacement.exists():
            raise UserError("Selected replacement swap device does not exist.")
        self.write(
            {
                "is_swap_out": True,
                "swap_device_id": replacement.id,
                "swap_reason": reason,
                "swap_condition_grade": grade,
                "swap_logistics_status": "dispatched",
            }
        )
        self.message_post(
            body=f"FR-SRM-064: Asset swap triggered. Replacement device {replacement.name} "
            f"assigned with reason '{reason}' and condition '{grade}'."
        )
        self._emit("service_order.device_swapped", self)

    def action_defer_order(self, reason="parts_backorder", resume_date=None, notes=None):
        """Pause active SLA clocks and record deferred hold."""
        self.ensure_one()
        self.write(
            {
                "is_deferred_block": True,
                "deferred_reason": reason,
                "deferred_until": resume_date,
                "deferred_notes": notes,
                "sla_clock_paused": True,
            }
        )
        self.message_post(
            body=f"Deferred repair hold activated: {reason}. Resumption target: {resume_date or 'Indefinite'}."
        )
        self._emit("service_order.deferred", self)

    def action_resume_order(self):
        """Resume repair order and restart SLA clock."""
        self.ensure_one()
        self.write(
            {
                "is_deferred_block": False,
                "sla_clock_paused": False,
            }
        )
        self.message_post(body="Deferred repair hold lifted — order processing resumed.")
        self._emit("service_order.resumed", self)

    # --- Idempotency (T08, DI-04) ---
    @api.model_create_multi
    def create(self, vals_list):
        # DI-04: a vals whose idempotency key already exists yields the existing
        # order instead of a new one. Per vals, in input order: the old body
        # RETURNED on the first replayed key, silently dropping every other vals
        # of the batch.
        result_ids = []  # existing order id, or None for "created below"
        to_create = []
        for vals in vals_list:
            key = vals.get("idempotency_key")
            existing = key and self.search([("idempotency_key", "=", key)], limit=1)
            if existing:
                result_ids.append(existing.id)
                continue
            if not key:
                vals["idempotency_key"] = str(uuid.uuid4())
            if not vals.get("name"):
                # The old field default fell back to the literal "NEW" when the
                # sequence was missing: 825 orders in fix_dev shared that
                # reference. A missing sequence must stop the create instead.
                ref = self.env["ir.sequence"].next_by_code("fix.service.order")
                if not ref:
                    raise UserError(
                        "The 'fix.service.order' sequence is missing — cannot assign "
                        "a service order reference."
                    )
                vals["name"] = ref
            result_ids.append(None)
            to_create.append(vals)
        records = super().create(to_create)
        for rec in records:
            rec._check_warranty_gate()
            rec._flag_rework()
            rec._emit("service_order.created", rec)
        created = iter(records.ids)
        return self.browse([rid or next(created) for rid in result_ids])

    def _check_warranty_gate(self):
        """BRU-SRM-02 / WTY-01 (H): a warranty-type order can only be
        created while the device's warranty is ACTIVE at the request date,
        decided by the device (fix.device.is_under_warranty).

        The gate used to compare fix.device.warranty_status with "active", a
        value that field never takes ("in_warranty", "out_of_warranty",
        "extended", "unknown"): EVERY warranty order was refused - from the P01
        customer booking and the P04 corporate request alike (R01 re-audit
        2026-10-22)."""
        request_date = fields.Date.today()
        for order in self:
            if order.order_category != "warranty":
                continue
            device = order.device_id
            if not device.is_under_warranty(request_date):
                raise UserError(
                    "BRU-SRM-02: device %s has no active warranty on %s (warranty status "
                    "'%s') — a warranty order needs an ACTIVE warranty at the request date"
                    % (device.display_name, request_date, device.warranty_status or "unknown")
                )

    def _flag_rework(self):
        """BRU-SRM-06 (C): a new order for the same device with the same
        fault within 30 days is auto-flagged as rework and linked."""
        from datetime import timedelta

        cutoff = fields.Date.today() - timedelta(days=30)
        for order in self:
            if order.is_rework:
                continue
            original = self.search(
                [
                    ("device_id", "=", order.device_id.id),
                    ("id", "!=", order.id),
                    ("state", "not in", ("cancelled",)),
                    ("create_date", ">=", cutoff),
                ],
                order="create_date desc",
                limit=1,
            )
            if original:
                order.write({"is_rework": True, "rework_of_id": original.id})
                order.message_post(
                    body=(
                        "BRU-SRM-06: flagged as rework — device returned within 30 "
                        "days (linked to %s)" % original.name
                    )
                )

    def _emit(self, event_type: str, rec) -> None:
        from libs.py.fix_events import publish

        publish(
            self.env,
            event_type,
            "fix.service.order",
            rec.id,
            {
                "order_id": rec.id,
                "name": rec.name,
                "device_id": rec.device_id.id,
                "customer_id": rec.customer_id.id,
                "state": rec.state,
            },
        )
