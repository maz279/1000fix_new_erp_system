# fix.service.order — the flagship model (P04-M03-T02, CD-M01-01).
# Full state machine per AS-06 (declared in ONE place, DP-01).
# SLA computation delegated to services/sla-engine/ (AR-007 section 3.1).
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

import logging
import uuid

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
    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit",
                                        index=True)

    # Identity
    name = fields.Char(string="Order Reference", readonly=True, index=True,
                       default=lambda self: self.env["ir.sequence"].next_by_code(
                           "fix.service.order") or "NEW")
    idempotency_key = fields.Char(string="Idempotency Key", index=True, copy=False,
                                  help="DI-04: a retried POST must not create two orders")

    # The device (M17 registry)
    device_id = fields.Many2one("fix.device", string="Device", required=True,
                                ondelete="restrict", index=True)
    device_serial = fields.Char(related="device_id.serial_number", store=True,
                                string="S/N")

    # The customer (M33 party kernel)
    customer_id = fields.Many2one("res.partner", string="Customer", required=True,
                                  ondelete="restrict", index=True)
    customer_phone = fields.Char(related="customer_id.phone", string="Phone")

    # Branch and assignment
    branch_id = fields.Many2one("fix.branch", string="Branch", required=True,
                                ondelete="restrict")
    technician_id = fields.Many2one("hr.employee", string="Assigned Technician")

    # State machine (AS-06/DP-01: the declared transitions above are the authority)
    state = fields.Selection(SERVICE_ORDER_STATES, default="draft",
                             required=True, tracking=True, index=True,
                             group_expand="_read_group_states")

    # Service details
    service_type = fields.Selection(
        [("walk_in", "Walk-in"), ("collection", "Collection/Delivery"),
         ("onsite", "On-site"), ("mail_in", "Mail-in"), ("corporate", "Corporate/Bulk")],
        required=True, default="walk_in", tracking=True)
    # BRU-SRM-02/03: the commercial classification gating creation
    order_category = fields.Selection(
        [("standard", "Standard (Paid)"), ("warranty", "Warranty"),
         ("amc", "AMC / Contract"), ("rework", "Rework")],
        string="Order Category", default="standard", required=True, tracking=True,
        help="Warranty orders require an ACTIVE warranty at the request date "
             "(BRU-SRM-02); AMC orders require the device on an active contract's "
             "covered-asset list (BRU-SRM-03 — contracts land in Phase 7)")
    is_rework = fields.Boolean(
        string="Rework", default=False, copy=False, tracking=True,
        help="BRU-SRM-06: auto-flagged when the same device returns with the same "
             "fault within 30 days; linked to the original order")
    rework_of_id = fields.Many2one("fix.service.order", string="Rework Of",
                                   copy=False, index=True, readonly=True)
    fault_description = fields.Text(string="Fault Description", required=True,
                                    tracking=True)
    catalog_item_id = fields.Many2one("fix.catalogue.item", string="Service Catalogue Item")
    priority = fields.Selection(
        [("normal", "Normal"), ("high", "High"), ("urgent", "Urgent"), ("emergency", "Emergency")],
        default="normal", required=True, tracking=True)

    # SLA (T04: clocks and escalation — computation in services/sla-engine/)
    sla_policy_id = fields.Many2one("fix.sla.policy", string="SLA Policy")
    sla_response_deadline = fields.Datetime(readonly=True)
    sla_resolution_deadline = fields.Datetime(readonly=True)
    sla_response_at = fields.Datetime(readonly=True)
    sla_resolution_at = fields.Datetime(readonly=True)
    sla_clock_paused = fields.Boolean(default=False,
                                      help="Clock paused during customer hold or parts wait")

    # Related records
    estimate_ids = fields.One2many("fix.estimate", "order_id", string="Estimates")
    work_order_ids = fields.One2many("fix.work.order", "order_id", string="Work Orders")
    qc_checklist_ids = fields.One2many("fix.qc.checklist", "order_id", string="QC Checklists")

    # MIG-03: legacy reference (permanent)
    legacy_reference = fields.Char(string="Legacy Reference", index=True,
                                   help="MIG-03: the legacy system's order number, permanently retained")

    active = fields.Boolean(default=True)

    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _idempotency_key_unique = models.Constraint('UNIQUE (idempotency_key)', 'An order with this idempotency key already exists (DI-04 idempotency).')

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
                f"Valid transitions from '{old}': {', '.join(sorted(valid_targets)) or '(terminal state)'}")

    def write(self, vals):
        if "state" in vals:
            for rec in self:
                rec._validate_transition(vals["state"])
        result = super().write(vals)
        if "state" in vals:
            for rec in self:
                rec._on_state_change(vals["state"])
        return result

    def _on_state_change(self, new_state: str) -> None:
        """Hook for side effects on state changes."""
        self._emit(f"service_order.{new_state}", self)
        self.device_id.add_history(
            "service_order",
            f"Order {self.name}: {self.state} -> {new_state}",
            order_id=self.id)
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
        quality checklist — a hard gate, not a warning."""
        for order in self:
            checklists = order.qc_checklist_ids
            if not checklists:
                raise UserError(
                    "Order %s has no QC checklist — Ready requires one (BRU-SRM-04)"
                    % order.name)
            failed = checklists.filtered(lambda c: c.state != "passed")
            if failed:
                raise UserError(
                    "Order %s cannot be Ready: %d QC checklist(s) not passed (BRU-SRM-04)"
                    % (order.name, len(failed)))
        self.state = "ready"

    def action_deliver(self):
        self.state = "delivered"

    def action_close(self):
        self.state = "closed"

    def action_cancel(self):
        self.state = "cancelled"

    # --- Idempotency (T08, DI-04) ---
    @api.model_create_multi
    def create(self, vals_list):
        # DI-04: if an idempotency key is provided and an order already
        # exists with it, return the existing order instead of creating a new one
        for vals in vals_list:
            if vals.get("idempotency_key"):
                existing = self.search([("idempotency_key", "=", vals["idempotency_key"])], limit=1)
                if existing:
                    return existing
            if not vals.get("idempotency_key"):
                vals["idempotency_key"] = str(uuid.uuid4())
        records = super().create(vals_list)
        for rec in records:
            rec._check_warranty_gate()
            rec._flag_rework()
            rec._emit("service_order.created", rec)
        return records

    def _check_warranty_gate(self):
        """BRU-SRM-02 / WTY-01 (H): a warranty-type order can only be
        created while the device's warranty is ACTIVE at the request date.
        The device model computes the status; the gate reads it."""
        for order in self:
            if order.order_category != "warranty":
                continue
            status = order.device_id.warranty_status
            if status != "active":
                raise UserError(
                    "BRU-SRM-02: device %s warranty is '%s' — a warranty order "
                    "needs an ACTIVE warranty at the request date"
                    % (order.device_id.display_name, status or "none"))

    def _flag_rework(self):
        """BRU-SRM-06 (C): a new order for the same device with the same
        fault within 30 days is auto-flagged as rework and linked."""
        from datetime import timedelta
        cutoff = fields.Date.today() - timedelta(days=30)
        for order in self:
            if order.is_rework:
                continue
            original = self.search([
                ("device_id", "=", order.device_id.id),
                ("id", "!=", order.id),
                ("state", "not in", ("cancelled",)),
                ("create_date", ">=", cutoff),
            ], order="create_date desc", limit=1)
            if original:
                order.write({"is_rework": True, "rework_of_id": original.id})
                order.message_post(body=(
                    "BRU-SRM-06: flagged as rework — device returned within 30 "
                    "days (linked to %s)" % original.name))

    def _emit(self, event_type: str, rec) -> None:
        from libs.py.fix_events import publish
        publish(self.env, event_type, "fix.service.order", rec.id, {
            "order_id": rec.id,
            "name": rec.name,
            "device_id": rec.device_id.id,
            "customer_id": rec.customer_id.id,
            "state": rec.state,
        })
